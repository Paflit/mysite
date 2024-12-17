from django.shortcuts import render
from .models import Employee, Score, Expert, Score_Self
import pandas as pd
from django.utils import timezone
from django.db.models import Sum, F, Window, Count
from django.db.models.functions import RowNumber
from django.db.models import Avg
from .forms import UploadFileForm
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

from .filters import EmployeeFilter



def accept_init(request):
    if request.method == 'POST':
        data = request.POST

        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        job_title = data.get('job_title')
        department = data.get('department')
        project = data.get('project')
        role_in_project = data.get('role_in_project')
        init = data.get('init')
        score = 0


        # Получаем сумму полей для конкретного проекта
        result = Score_Self.objects.filter(project_name=project).aggregate(
            total_points=Sum('time_project_points') +
                         Sum('crossfunction_points') +
                         Sum('budget_points') +
                         Sum('volume_doc_points') +
                         Sum('scalability_points') +
                         Sum('income_project_ponts') +
                         Sum('tarif_points')
        )

        # Извлекаем сумму из результата
        total_points = result['total_points'] if result['total_points'] is not None else 0


        if init == 'Да':
            init = True
            score += 50
            total_points += 50
        elif init == 'Нет':
            init = False
        else:
            init = False
        if role_in_project in ['Лидер', 'Участник']:
            if role_in_project == 'Лидер':
                score += 25
            elif role_in_project == 'Участник':
                score += 15

            if not Employee.objects.filter(last_name=last_name, first_name=first_name,
                                           middle_name=middle_name, job_title=job_title,
                                           department=department, project=project).exists():
                Employee.objects.create(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    job_title=job_title,
                    department=department,
                    project=project,
                    time_created=timezone.now,
                    init = init,
                    role_in_project=role_in_project,
                    personal_score = score)

                # Фильтруем сотрудника по полям имени, должности и отдела
                Employee.objects.filter(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    job_title=job_title,
                    department=department
                ).update(score=F('score') + total_points)


        elif role_in_project in ['Эксперт', 'Куратор']:
            if not Expert.objects.filter(last_name=last_name, first_name=first_name,
                                           middle_name=middle_name, job_title=job_title,
                                           department=department, project=project).exists():
                Expert.objects.create(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    job_title=job_title,
                    department=department,
                    project=project,
                    time_created=timezone.now,
                    init = init,
                    role_in_project=role_in_project,
                    personal_score = score)

                # Фильтруем сотрудника по полям имени, должности и отдела
                Expert.objects.filter(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    job_title=job_title,
                    department=department
                ).update(score=F('score') + total_points)







    return render(request, 'blog/accept_init.html')
def choice_project(request):
    return render(request, 'blog/choice_project.html')

def form_init(request):

    employees = Employee.objects.all().filter(active=True).values('last_name', 'first_name', 'middle_name').annotate(
        score=Sum('score')).order_by('-score')
    employees = employees.annotate(
        number=Window(
            expression=RowNumber(),
            order_by=F('score').desc()
        )
    ).values('number', 'last_name', 'first_name', 'middle_name', 'job_title', 'department', 'score', 'time_created')
    all_objects = Employee.objects.all()
    all_project = Score_Self.objects.all()
    last_names = []
    first_names = []
    middle_names = []
    departments = []
    job_titles = []
    projects = []
    for employee in all_objects:
        last_names.append(employee.last_name)
        first_names.append(employee.first_name)
        middle_names.append(employee.middle_name)
        departments.append(employee.department)
        job_titles.append(employee.job_title)
    for project in all_project:
        projects.append(project.project_name)
    first_names = list(set(first_names))
    middle_names = list(set(middle_names))
    departments = list(set(departments))
    job_titles = list(set(job_titles))
    return render(request, 'blog/form_init.html', {'employees': employees, 'last_names': last_names,
                                              'first_names': first_names, 'middle_names': middle_names,
                                              'departments': departments, 'job_titles': job_titles, 'projects':projects})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST)
        if form.is_valid():
            handle_upload_file(form.cleaned_data['file'])
    else:
        form = UploadFileForm()

    return render(request, 'blog/upload_file.html', {'form': form})

def register_project(request):
    return render(request, 'blog/register_project.html')

from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings
from .models import Score_Self, Employee
import os

def register_accept(request):
    if request.method == 'POST':
        data = request.POST
        uploaded_file = request.FILES.get('presentation')  # Получаем загруженный файл

        # Проверка размера файла (до 5 МБ)
        if uploaded_file and uploaded_file.size > 5 * 1024 * 1024:
            return HttpResponse("Ошибка: размер файла превышает 5 МБ!")

        # Получаем данные из формы
        name_project = data.get('name_project')
        project = data.get('project')
        category_project = data.get('category_project')
        time_project = data.get('time_project')
        crossfunction = data.get('crossfunction')
        company_partner = data.get('company_partner')
        budget = data.get('budget')
        volume_doc = data.get('volume_doc')
        scalability = data.get('scalability')
        income_project = data.get('income_project')
        tarif = data.get('tarif')
        effect = data.get('effect')
        timeline = data.get('timeline')

        # Подсчёт баллов
        time_project_points = {'до 12 месяцев': 1, '12-24 месяца': 2, 'более 24': 3}.get(time_project, 0)
        crossfunction_points = {'до 2': 1, '3-4': 2, 'более 5': 3}.get(crossfunction, 0)
        company_partner_points = {
            'только подразделения ОАО "РЖД"': 1,
            'подразделения ОАО "РЖД" и 1 компания-партнер': 2,
            'подразделения ОАО "РЖД" и 2 или более компании-партнеры': 3
        }.get(company_partner, 0)
        budget_points = {'Без вложений': 1, '0-5 млн. рублей': 2, 'более 5 млн. рублей': 3}.get(budget, 0)
        volume_doc_points = {'до 10': 1, '10-20': 2, 'более 20': 3}.get(volume_doc, 0)
        scalability_points = {
            'Проект уровня ОАО "РЖД"': 1,
            'Проект федерального уровня': 2,
            'Проект международного уровня': 3
        }.get(scalability, 0)
        income_project_points = {'до 1 млн. рублей': 1, 'от 1 до 5 млн. рублей': 2, 'более 5 млн. рублей': 3}.get(income_project, 0)
        tarif_points = {'до 10 млн. рублей': 1, 'от 10 до 30 млн. рублей': 2, 'более 30 млн. рублей': 3}.get(tarif, 0)

        # Подсчёт итогового балла
        project_score = 0
        if category_project == 'Проект собственного авторства':
            project_score += 50 if timeline == 'Да' else 40
            effect_points = {'До 100 млн. руб': 10, '100-500 млн. руб': 20, '500 млн. руб - 1 млрд. руб': 30, 'более 1 млрд. руб': 40}
            project_score += effect_points.get(effect, 0)

            # Проверка и сохранение записи
            if not Score_Self.objects.filter(project_name=name_project).exists():
                Score_Self.objects.create(
                    project_name=name_project,
                    project=project,
                    project_score=project_score,
                    time_project_points=time_project_points,
                    crossfunction_points=crossfunction_points,
                    budget_points=budget_points,
                    volume_doc_points=volume_doc_points,
                    scalability_points=scalability_points,
                    income_project_ponts=income_project_points,
                    tarif_points=tarif_points
                )

        # Обновление баллов сотрудников
        employees = Employee.objects.filter(project=name_project)
        score_elem = Score_Self.objects.filter(project_name=name_project)

        type_project = 'S' if project_score <= 14 else 'M' if project_score <= 17 else 'L'

        for employee in employees:
            employee.score = project_score + employee.personal_score
            employee.save()
        for elem in score_elem:
            elem.type_project = type_project
            elem.save()

        # Формируем текст письма
        message = f"""
        Название проекта: {name_project}
        Описание проекта: {project}
        Итоговый балл проекта: {project_score}
        Категория проекта: {category_project}
        Время реализации: {time_project}
        Кроссфункциональность: {crossfunction}
        Компании-партнеры: {company_partner}
        Бюджет: {budget}
        Объём документов: {volume_doc}
        Масштабирование: {scalability}
        Доходы: {income_project}
        Тариф: {tarif}
        Эффект: {effect}
        Сроки реализации: {timeline}
        Тип проекта: {type_project}
        """

        # Отправка письма с вложением
        email = EmailMessage(
            subject=f"Новая заявка на проект: {name_project}",
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=['ya.gplnsk@gmail.com']
        )

        # Если есть загруженный файл, прикрепляем его
        if uploaded_file:
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

        email.send(fail_silently=False)

        return HttpResponse("Заявка успешно обработана и отправлена на почту!")

    return render(request, 'blog/register_accept.html')

def handle_upload_file(f):
    with open(f"uploads/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
def add_rating_expert(request):
    if request.method == 'POST':
        data = request.POST
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        job_title = data.get('job_title')
        department = data.get('department')
        project = data.get('project')
        role_in_project = data.get('role_in_project')

        if not Expert.objects.filter(last_name=last_name, first_name=first_name,
                                       middle_name=middle_name, job_title=job_title,
                                       department=department, project=project).exists():
            Expert.objects.create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                job_title=job_title,
                department=department,
                project=project,
                time_created=timezone.now(),
                role_in_project=role_in_project,
                active=True  # Не забудьте установить это поле
            )

    # Применяем фильтр
    filter = EmployeeFilter(request.GET, queryset=Expert.objects.filter(active=True))
    employees = filter.qs

    # Группируем и аннотируем данные
    employees = employees.values(
        'last_name', 'first_name', 'middle_name', 'job_title', 'department'
    ).annotate(
        total_score=Sum('score'),
        project_count=Count('project', distinct=True)
    ).order_by('-total_score')

    # Сортируем по total_score и добавляем нумерацию строк
    employees = employees.annotate(
        row_number=Window(
            expression=RowNumber(),
            order_by=F('total_score').desc()
        )
    )

    # Выбираем поля для вывода
    employees = employees.values(
        'row_number', 'last_name', 'first_name', 'middle_name', 'job_title', 'total_score',
        'project_count'
    )
    print(employees)
    return render(request, 'blog/table_expert.html', {'employees': employees, 'filter': filter})

def add_rating(request):
    if not Employee.objects.exists():
        excel_file = r'C:\Users\yhate\Downloads\rating.xlsx'
        if excel_file.endswith('.xls') or excel_file.endswith('.xlsx'):
            df = pd.read_excel(excel_file)
            for index, row in df.iterrows():
                Employee.objects.create(
                    number=row['Место в рейтинге'],
                    last_name=row['Фамилия'],
                    first_name=row['Имя'],
                    middle_name=row['Отчество'],
                    job_title=row['Должность'],
                    department=row['Место работы'],
                    project=row['Проект'],  # Обратите внимание, добавьте это поле если оно есть в Excel
                    score=row['Итоговая оценка'],
                    active=True
                )

    elif request.method == 'POST':
        data = request.POST
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        job_title = data.get('job_title')
        department = data.get('department')
        project = data.get('project')
        role_in_project = data.get('role_in_project')

        if not Employee.objects.filter(last_name=last_name, first_name=first_name,
                                       middle_name=middle_name, job_title=job_title,
                                       department=department, project=project).exists():
            Employee.objects.create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                job_title=job_title,
                department=department,
                project=project,
                time_created=timezone.now(),
                role_in_project=role_in_project,
                active=True  # Не забудьте установить это поле
            )

    # Применяем фильтр
    filter = EmployeeFilter(request.GET, queryset=Employee.objects.filter(active=True))
    employees = filter.qs

    # Группируем и аннотируем данные
    employees = employees.values(
        'last_name', 'first_name', 'middle_name', 'job_title', 'department'
    ).annotate(
        total_score=Sum('score'),
        project_count=Count('project', distinct=True)
    ).order_by('-total_score')

    # Сортируем по total_score и добавляем нумерацию строк
    employees = employees.annotate(
        row_number=Window(
            expression=RowNumber(),
            order_by=F('total_score').desc()
        )
    )

    # Выбираем поля для вывода
    employees = employees.values(
        'row_number', 'last_name', 'first_name', 'middle_name', 'job_title', 'total_score',
        'project_count'
    )
    print(employees)
    return render(request, 'blog/table.html', {'employees': employees, 'filter': filter})



def forms(request):
    if request.method == 'POST':
        data = request.POST
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        job_title = data.get('job_title')
        department = data.get('department')
        project = data.get('project')
        role_in_project = data.get('role_in_project')

        if not Employee.objects.filter(last_name=last_name, first_name=first_name,
                                       middle_name=middle_name, job_title=job_title,
                                       department=department, project=project).exists():
            Employee.objects.create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                job_title=job_title,
                department=department,
                project=project,
                time_created=timezone.now,
                role_in_project=role_in_project)

    employees = Employee.objects.all().filter(active=True).values('last_name', 'first_name', 'middle_name').annotate(
        score=Sum('score')).order_by('-score')
    employees = employees.annotate(
        number=Window(
            expression=RowNumber(),
            order_by=F('score').desc()
        )
    ).values('number', 'last_name', 'first_name', 'middle_name', 'job_title', 'department', 'score')
    all_objects = Employee.objects.all()
    last_names = []
    first_names = []
    middle_names = []
    departments = []
    job_titles = []
    for employee in all_objects:
        last_names.append(employee.last_name)
        first_names.append(employee.first_name)
        middle_names.append(employee.middle_name)
        departments.append(employee.department)
        job_titles.append(employee.job_title)
    first_names = list(set(first_names))
    middle_names = list(set(middle_names))
    departments = list(set(departments))
    job_titles = list(set(job_titles))
    return render(request, 'blog/kyky.html', {'employees': employees, 'last_names': last_names,
                                               'first_names': first_names, 'middle_names': middle_names,
                                               'departments': departments, 'job_titles': job_titles})


def accept(request):
    if request.method == 'POST':
        data = request.POST
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        job_title = data.get('job_title')
        department = data.get('department')
        project = data.get('project')
        role_in_project = data.get('role_in_project')


        score = 0
        if role_in_project == 'Лидер':
            score += 20
        elif role_in_project == 'Участник':
            score += 10

        if not Employee.objects.filter(last_name=last_name, first_name=first_name,
                                       middle_name=middle_name, job_title=job_title,
                                       department=department, project=project).exists():
            Employee.objects.create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                job_title=job_title,
                department=department,
                project=project,
                time_created=timezone.now,
                role_in_project=role_in_project,
                personal_score = score)


    return render(request, 'blog/accept.html')


def graduate(request):
    return render(request, 'blog/graduate.html')


def score_accept(request):
    if request.method == 'POST':
        data = request.POST
        name_project = data.get('name_project')
        fio = data.get('fio')
        time_project = data.get('time_project')
        crossfunction = data.get('crossfunction')
        company_partner = data.get('company_partner')
        budget = data.get('budget')
        volume_doc = data.get('volume_doc')
        scalability = data.get('scalability')
        income_project = data.get('income_project')
        tarif = data.get('tarif')
        expert_score = data.get('expert_score')
        effect = data.get('effect')
        timeline = data.get('timeline')
        category_project = data.get('category_project')
        summary_points = 0
        if time_project == 'до 12 месяцев':
            summary_points += 1
        elif time_project == '12-24 месяца':
            summary_points += 2
        elif time_project == 'более 24':
            summary_points += 3
        if crossfunction == 'до 2':
            summary_points += 1
        elif crossfunction == '3-4':
            summary_points += 2
        elif crossfunction == 'более 5':
            summary_points += 3
        if company_partner == 'только подразделения ОАО "РЖД"':
            summary_points += 1
        elif company_partner == 'подразделения ОАО "РЖД" и 1 компания-партнер':
            summary_points += 2
        elif company_partner == 'подразделения ОАО "РЖД" и 2 или более компании-партнеры':
            summary_points += 3
        if budget == 'Без вложений':
            summary_points += 1
        elif budget == '0-5 млн. рублей':
            summary_points += 2
        elif budget == 'более 5 млн. рублей':
            summary_points += 3
        if volume_doc == 'до 10':
            summary_points += 1
        elif volume_doc == '10-20':
            summary_points += 2
        elif volume_doc == 'более 20':
            summary_points += 3
        if scalability == 'Проект уровня ОАО "РЖД"':
            summary_points += 1
        elif scalability == 'Проект федерального уровня':
            summary_points += 2
        elif scalability == 'Проект международного уровня':
            summary_points += 3
        if income_project == 'до 1 млн. рублей':
            summary_points += 1
        elif income_project == 'от 1 до 5 млн. рублей':
            summary_points += 2
        elif income_project == 'более 5 млн. рублей':
            summary_points += 3
        if tarif == 'до 10 млн. рублей':
            summary_points += 1
        elif tarif == 'от 10 до 30 млн. рублей':
            summary_points += 2
        elif tarif == 'более 30 млн. рублей':
            summary_points += 3
        if expert_score == 1:
            summary_points += 1
        elif expert_score == 2:
            summary_points += 2
        elif expert_score == 3:
            summary_points += 3
        project_score = 0
        if category_project == 'Проект собственного авторства':
            if timeline == 'Да':
                project_score += 50
            elif timeline == 'Нет':
                project_score += 40
            if effect == 'До 100 млн. руб':
                project_score += 10
            elif effect == '100-500 млн. руб':
                project_score += 20
            elif effect == '500 млн. руб - 1 млрд. руб':
                project_score += 30
            elif effect == 'более 1 млрд. руб':
                project_score += 40
        elif category_project == 'Проект из базы ПД':
            if timeline == 'Да':
                project_score += 40
            elif timeline == 'Нет':
                project_score += 30
            if effect == 'До 100 млн. руб':
                project_score += 5
            elif effect == '100-500 млн. руб':
                project_score += 10
            elif effect == '500 млн. руб - 1 млрд. руб':
                project_score += 20
            elif effect == 'более 1 млрд. руб':
                project_score += 30
        Score.objects.create(project_name=name_project, fio = fio, score=summary_points, project_score = project_score)

        avg_score = Score.objects.filter(project_name=name_project).aggregate(avg_score=Avg('score'))['avg_score']
        average_score = Score.objects.filter(project_name=name_project).aggregate(avg_score=Avg('project_score'))['avg_score']
        employees = Employee.objects.all().filter(project=name_project)
        score_elem = Score.objects.all().filter(project_name=name_project)

        if avg_score <= 14:
            type_project = 'S'
        elif avg_score > 14 and avg_score <= 17:
            type_project = 'M'
        elif avg_score > 17:
            type_project = 'L'
        for employee in employees:
            employee.score = average_score + employee.personal_score
            employee.save()
        for elem in score_elem:
            elem.type_project = type_project
            elem.save()
    return render(request, 'blog/score_accept.html')




