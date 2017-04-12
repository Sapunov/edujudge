from django.contrib import admin
from judge.api.models import Task, Test, Check, Comment


class TestAdmin(admin.ModelAdmin):

    readonly_fields = ('seqnum',)

admin.site.register(Task)
admin.site.register(Test, TestAdmin)
admin.site.register(Check)
admin.site.register(Comment)
