from django.contrib import admin
from judge.api.models import (
    Task, Solution, Comment,
    Test, Example, Notification)


class CommentAdmin(admin.ModelAdmin):

    list_display = ('id', 'task', 'user', 'task_owner', 'text', 'time')
    ordering = ('-id',)


class SolutionAdmin(admin.ModelAdmin):

    list_display = ('id', 'task', 'user', 'error', 'test', 'time')
    ordering = ('-id',)
    readonly_fields = ('task', 'test', 'user', 'source')
    exclude = ('source_path',)

class TaskAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'author', 'test_checker_path', 'show')
    ordering = ('-id',)
    readonly_fields = ('checker_source',)

class NotificationAdmin(admin.ModelAdmin):

    list_display = ('id', 'kind', 'time', 'user_from', 'user_for', 'seen')
    ordering = ('-id',)


admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Test)
admin.site.register(Example)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(Notification, NotificationAdmin)
