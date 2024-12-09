from django.db import models



class Employee(models.Model):
    number = models.IntegerField(default=0)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=255)
    department = models.CharField(max_length=255) 
    score = models.IntegerField(default=0)
    personal_score = models.IntegerField(default=0)
    project = models.CharField(max_length=255, default='')
    role_in_project = models.CharField(max_length=255, default='')
    init = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


    class Meta:
        verbose_name = 'Рейтинг ПД'
        verbose_name_plural = 'Рейтинг ПД'
        ordering = ['active']

class Expert(models.Model):
    number = models.IntegerField(default=0)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    personal_score = models.IntegerField(default=0)
    project = models.CharField(max_length=255, default='')
    role_in_project = models.CharField(max_length=255, default='')
    init = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    class Meta:
        verbose_name = 'Рейтинг ПД'
        verbose_name_plural = 'Рейтинг ПД'
        ordering = ['active']

class Score(models.Model):
    project_name = models.CharField(max_length=200)
    fio = models.CharField(max_length=200, default='')
    score = models.IntegerField(default=0)
    project_score = models.IntegerField(default=0)
    type_project = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"{self.project_name}"

    class Meta:
        verbose_name = 'Оценка проектов'
        verbose_name_plural = 'Оценка проектов'

class Selfmadeprojects(models.Model):
    project_name = models.CharField(max_length=200)
    project_score = models.IntegerField(default=0)
    type_project = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"{self.project_name}"

    class Meta:
        verbose_name = 'Оценка проектов'
        verbose_name_plural = 'Оценка проектов'


class Score_Self(models.Model):
    project_name = models.CharField(max_length=200)
    project = models.CharField(max_length=200)
    project_score = models.IntegerField(default=0)
    type_project = models.CharField(max_length=200, default='')
    time_project_points = models.IntegerField(default=0)
    crossfunction_points = models.IntegerField(default=0)
    budget_points = models.IntegerField(default=0)
    volume_doc_points = models.IntegerField(default=0)
    scalability_points = models.IntegerField(default=0)
    income_project_ponts = models.IntegerField(default=0)
    tarif_points = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.project_name}"

    class Meta:
        verbose_name = 'Оценка проектов'
        verbose_name_plural = 'Оценка проектов'