import os
import errno

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
    test_generator_path = models.FilePathField(
        path=settings.TEST_GENERATORS_DIR, blank=True, null=True)

    @classmethod
    def all_with_user_solution(cls, user):

        tasks = cls.objects.all().order_by('id')
        for i in range(len(tasks)):
            solutions = tasks[i].solutions.filter(user=user).order_by('error')
            if solutions.count() == 0:
                tasks[i].solved = -1
            elif solutions[0].error == 0:
                tasks[i].solved = 1
            else:
                tasks[i].solved = 0

        return tasks

    @staticmethod
    def get_test_generator_path(user):

        return os.path.join(
            settings.TEST_GENERATORS_DIR,
            'testgenerator_{user_id}_{date}.py'.format(
                user_id=user.id,
                date=datetime.now().strftime('%Y%m%d_%H%M%S')
            )
        )

    @staticmethod
    def save_test_generator(source, path):

        with open(path, 'w') as fd:
            fd.write(source)

        return path

    @staticmethod
    def remove_test_generator(path):

        try:
            os.remove(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    def __str__(self):

        return 'Task #{0}: {1}'.format(self.id, self.title)

    class Meta:

        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class Example(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField()
    answer = models.TextField()

    def __str__(self):

        return 'Example #{0} for task #{1}'.format(self.id, self.task.id)

    class Meta:

        verbose_name = 'Example'
        verbose_name_plural = 'Examples'


class Test(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tests')
    text = models.TextField()
    answer = models.TextField()

    def __str__(self):

        return 'Test #{0} for task #{1}'.format(self.id, self.task.id)

    class Meta:

        verbose_name = 'Test'
        verbose_name_plural = 'Tests'


class Solution(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, default=None, null=True)
    testnum = models.SmallIntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    source_path = models.FilePathField(path=settings.SOURCE_DIR)
    error = models.SmallIntegerField(default=0)
    verdict = models.TextField(default=None, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')

    @classmethod
    def fetch_solutions(cls, tasks, users, limit=-1):

        solutions = Solution.objects.filter(
            user__in=users,
            task__in=tasks).order_by('-time')

        if len(users) == 1 and limit > 0:
            solutions = solutions[:limit]

        for solution in solutions:
            if solution.test and len(solution.test.text) > settings.TEST_INPUT_MAX_LEN:
                solution.test.text = solution.test.text[:settings.TEST_INPUT_MAX_LEN]
                solution.test.text += ' <данные обрезаны из-за большого размера>'

        return solutions

    @classmethod
    def is_task_solved(cls, task_id, user):

        solutions = cls.objects.filter(task__id=task_id, user=user).order_by('error')

        if solutions.count() == 0:
            return -1
        elif solutions[0].error == 0:
            return 1
        else:
            return 0

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
            'usersource-{task_id}-{user_id}-{date}'.format(
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

    @property
    def error_description(self):

        return settings.TEST_ERRORS[self.error]

    def delete(self):

        os.remove(self.source_path)
        super(Solution, self).delete()

    def __str__(self):

        return 'Solution #{0} for task #{1} by <{2}>'.format(
            self.id, self.task.id, self.user,)

    class Meta:

        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'


class Comment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    task_owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    text = models.TextField()

    def __str__(self):

        return 'Comment #{0} by <{1}>: {2}'.format(self.id, self.user, self.text[:100])

    class Meta:

        verbose_name = 'Task comment'
        verbose_name_plural = 'Task comments'
