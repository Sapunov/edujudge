from datetime import datetime, timedelta
import errno
import logging
import os
import pytz

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Min
from django.utils import timezone

from judge.api import im


log = logging.getLogger('main.' + __name__)


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_active = models.DateTimeField(default=datetime(1970, 1, 1, tzinfo=pytz.utc))

    @classmethod
    def get_user_profile(cls, user):

        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            return profile

    def mark_active(self):

        self.last_active = timezone.now()
        self.save()

    @property
    def last_active_seconds(self):

        return int((timezone.now() - self.last_active).total_seconds())

    @classmethod
    def get_active_users(cls, delta, staff=False):

        assert isinstance(delta, timedelta), 'Delta must be timedelta'

        start_time = timezone.now() - delta
        profiles = cls.objects.filter(last_active__gte=start_time)

        if staff:
            return [p.user for p in profiles]
        else:
            return [p.user for p in profiles if not p.user.is_staff]

    @classmethod
    def get_online_users(cls, staff=False):

        return cls.get_active_users(timedelta(seconds=60 * 5), staff)


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
    test_checker_path = models.FilePathField(
        path=settings.TEST_CHECKERS_DIR, blank=True, null=True)

    @property
    def has_checker(self):

        return self.test_checker_path is not None

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
    def get_test_checker_path(user):

        return os.path.join(
            settings.TEST_CHECKERS_DIR,
            'testchecker_{user_id}_{date}.py'.format(
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
    def save_test_checker(source, path):

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

    @staticmethod
    def remove_test_checker(path):

        try:
            os.remove(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    @property
    def checker_source(self):

        if self.has_checker:
            with open(self.test_checker_path) as fd:
                return fd.read()
        return ''

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
    source_path = models.FilePathField(path=settings.SOURCE_DIR)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    time = models.DateTimeField(auto_now_add=True)
    # Fills after solution check
    test = models.ForeignKey(Test, on_delete=models.CASCADE, default=None, null=True)
    testnum = models.SmallIntegerField(default=0)
    error = models.SmallIntegerField(default=0)
    error_line = models.IntegerField(default=-1)
    verdict = models.TextField(default=None, null=True)

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
    def fetch_failed_with_users(cls, staff=False):

        params = {}

        if not staff:
            params['user__is_staff'] = False

        solutions = Solution.objects.filter(**params).values(
            'user_id', 'task_id').annotate(min_mark=Min('error'))

        user_ids = set()
        task_ids = set()

        for group in solutions:
            if group['min_mark'] > 0:
                user_ids.add(group['user_id'])
                task_ids.add(group['task_id'])

        return list(sorted(user_ids)), list(sorted(task_ids))

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
            return fd.read().split('\n')

    @property
    def error_description(self):

        return settings.TEST_ERRORS[self.error]

    def delete(self):

        os.remove(self.source_path)
        super(Solution, self).delete()

    def __str__(self):

        return 'Solution #{0} for task #{1} by <{2}>'.format(
            self.id, self.task.id, self.user)

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


class Notification(models.Model):

    KIND_CHOICES = (
        ('co', 'comment'),
    )

    time = models.DateTimeField(auto_now_add=True)
    user_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    kind = models.CharField(max_length=2, choices=KIND_CHOICES)
    html = models.CharField(max_length=1000, null=True, blank=True)
    seen = models.BooleanField(default=False)

    @classmethod
    def send(cls, user_for, user_from, kind, html=None, send_im=True, im_payload=None):

        notification = cls.objects.create(
            user_for=user_for,
            user_from=user_from,
            kind=kind,
            html=html)

        if send_im:
            try:
                im.send_message(
                    user_id=user_for.id,
                    msg_type=kind,
                    message=im_payload,
                    alert_msg=html,
                    notification_id=notification.id
                )
            except Exception as exc:
                log.exception(exc)

        # Увеличить счетчик в интерфейсе
        try:
            im.send_message(
                user_id=user_for.id,
                msg_type='unseen++'
            )
        except Exception as exc:
            log.exception(exc)

    @classmethod
    def send_many(cls, users_for, user_from, kind, html=None, send_im=True, im_payload=None):

        for user_for in users_for:
            cls.send(user_for, user_from, kind, html, send_im, im_payload)

    @classmethod
    def mark_seen(cls, messages_ids_or_id):

        if not isinstance(messages_ids_or_id, list):
            messages_ids_or_id = [messages_ids_or_id]

        cls.objects.filter(id__in=messages_ids_or_id).update(seen=True)

        for message in cls.objects.filter(id__in=messages_ids_or_id):
            try:
                im.send_message(
                    user_id=message.user_for.id,
                    msg_type='unseen--'
                )
            except Exception as exc:
                log.exception(exc)
