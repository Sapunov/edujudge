import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime


class Task(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField()
    initial_data = models.TextField()
    result = models.TextField()
    notes = models.TextField(null=True, blank=True)
    timelimit = models.SmallIntegerField()
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')

    def __str__(self):

        return self.title

    class Meta:

        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class Example(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField()
    answer = models.TextField()

    class Meta:

        verbose_name = 'Example'
        verbose_name_plural = 'Examples'


class Test(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tests')
    text = models.TextField()
    answer = models.TextField()

    def __str__(self):

        return '<Test #{0} for {1} task>'.format(self.id, self.task.id)

    class Meta:

        verbose_name = 'Test'
        verbose_name_plural = 'Tests'


class Solution(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, default=None, null=True)
    testnum = models.SmallIntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    source_path = models.FilePathField(path=settings.SOURCE_DIR)
    error = models.SmallIntegerField(default=0)
    verdict = models.TextField(default=None, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')

    @classmethod
    def create(cls, source, task, user):

        source_path = cls.get_source_path(task, user)

        cls.save_source(source, source_path)

        solution = cls.objects.create(
            task=task, user=user, source_path=source_path)

        return solution

    @staticmethod
    def get_source_path(task, user):

        return os.path.join(
            settings.SOURCE_DIR,
            '{task_id}-{user_id}-{date}'.format(
                task_id=task.id,
                user_id=user.id,
                date=datetime.now().strftime('%Y%m%d_%H%M%S')
            )
        )

    @staticmethod
    def save_source(source, path):

        with open(path, 'w') as fd:
            fd.write(source)

    @property
    def source(self):

        with open(self.source_path) as fd:
            return fd.read()

    def delete(self):

        os.remove(self.source_path)
        super(Solution, self).delete()

    def __str__(self):

        return '{0} - {1}'.format(self.user, self.task.title)


    class Meta:

        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'


class Comment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey('self')
    text = models.TextField()

    class Meta:

        verbose_name = 'Task comment'
        verbose_name_plural = 'Task comments'
