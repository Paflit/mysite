import django_filters
from django import forms
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.ChoiceFilter(
        field_name='department',
        lookup_expr='icontains',
        widget=forms.Select,
        choices=lambda: get_active_projects('department'),
        label='Подразделение:'
    )

    project = django_filters.ChoiceFilter(
        field_name='project',
        lookup_expr='icontains',
        widget=forms.Select,
        choices=lambda: get_active_projects('project'),
        label='Проект:'
    )

    class Meta:
        model = Employee
        fields = ['department', 'project']

def get_active_projects(field_name):
    active_projects = Employee.objects.filter(active=True).values_list(field_name, flat=True).distinct()
    return [(proj, proj) for proj in active_projects]
