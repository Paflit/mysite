from django.contrib import admin

from .models import *

class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['last_name', 'first_name', 'middle_name', 'project', 'active']
    list_display = ('time_created', 'last_name', 'first_name', 'middle_name', 'project', 'role_in_project' ,'personal_score', 'score','init', 'active')
    list_editable = ('active', 'score')
    ordering = ('active', '-score')

class ExpertAdmin(admin.ModelAdmin):
    search_fields = ['last_name', 'first_name', 'middle_name', 'project', 'active']
    list_display = ('time_created', 'last_name', 'first_name', 'middle_name', 'project', 'role_in_project' ,'personal_score', 'score','init', 'active')
    list_editable = ('active', 'score')
    ordering = ('active', '-score')
class ScoreAdmin(admin.ModelAdmin):
    search_fields = ['project_name']
    list_display = ('project_name', 'fio', 'score', 'project_score', 'type_project')

class ScoreSelfAdmin(admin.ModelAdmin):
    search_fields = ['project_name']
    list_display = ('project_name', 'project', 'project_score', 'type_project', 'time_project_points', 'crossfunction_points',
                    'budget_points', 'volume_doc_points', 'volume_doc_points', 'income_project_ponts', 'tarif_points')




admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Expert, ExpertAdmin)
admin.site.register(Score_Self, ScoreSelfAdmin)