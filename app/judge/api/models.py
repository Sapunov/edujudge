from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    title = models.CharField(max_length=100)
    text = models.TextField()
    tlimit = models.SmallIntegerField()
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')

    class Meta:

        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class Test(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.TextField()
    answer = models.TextField()
    seqnum = models.SmallIntegerField()

    class Meta:

        verbose_name = 'Test'
        verbose_name_plural = 'Tests'


class Check(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    iserror = models.BooleanField(default=False)
    verdict = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')

    class Meta:

        verbose_name = 'Check'
        verbose_name_plural = 'Checks'


class Comment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey('self')
    text = models.TextField()

    class Meta:

        verbose_name = 'Task comment'
        verbose_name_plural = 'Task comments'
