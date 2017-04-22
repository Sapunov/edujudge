from django.contrib import admin
from judge.api.models import Task, Solution, Comment, Test


admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Test)


class SolutionAdmin(admin.ModelAdmin):

    readonly_fields = ('task', 'test', 'user', 'source')
    exclude = ('source_path',)


admin.site.register(Solution, SolutionAdmin)
