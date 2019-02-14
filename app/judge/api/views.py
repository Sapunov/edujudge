from datetime import timedelta
import django_rq
import logging

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import (ValidationError, NotFound,
    PermissionDenied)

from judge.api import im
from judge.api import serializers
from judge.api.common import inflect_name, get_staff_ids, get_logger, get_staff
from judge.api.common import list_to_dict
from judge.api.im import get_user_messages
from judge.api.models import Task, Solution, Comment, Profile, Notification
from judge.api.serializers import serialize, deserialize
from judge.api.testcheckers import load_and_check_module
from judge.api.testgenerators import generate_tests
from judge.api.testsystem import test_solution


log = logging.getLogger('main.' + __name__)


class TasksListView(APIView):

    def get(self, request, format=None):
        """Список заданий
        """
        data = deserialize(
            serializers.UserInParamsSerializer,
            request.query_params
        ).data

        if 'user' in data:
            try:
                user = User.objects.get(username=data['user'])
            except User.DoesNotExist:
                raise NotFound()
        else:
            user = request.user

        tasks = Task.all_with_user_solution(user)
        serializer = serialize(serializers.TasksListSerializer, tasks, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        """Создание нового задания
        """
        if not request.user.is_staff:
            raise PermissionDenied()

        serializer = deserialize(serializers.TaskSerializer, data=request.data)
        serializer.save(user=request.user)

        return Response(status=status.HTTP_200_OK)


class TaskView(APIView):

    def get(self, request, task_id, format=None):
        """Отдает одно задание по идентификатору
        """
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        task.solved = Solution.is_task_solved(task_id, request.user)

        serializer = serialize(serializers.TaskOnlySerializer, task)

        return Response(serializer.data)


class TaskCheckView(APIView):

    def post(self, request, task_id, format=None):
        """Проверка задания
        """
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise ValidationError(
                'Task with id {0} does not exist'.format(task_id)
            )

        serializer = deserialize(serializers.TaskCheckSerializer, data=request.data)
        solution = serializer.save(user=request.user, task=task)

        django_rq.enqueue(test_solution, solution_id=solution.id)

        return Response(status=status.HTTP_200_OK)


class SolutionsListView(generics.GenericAPIView):

    serializer_class = serializers.SolutionsListParamsSerializer

    def create_solutions_summary(self, solutions):

        result = {}

        for solution in solutions:
            uid = solution.user_id
            tid = solution.task_id
            err = solution.error
            if uid in result:
                if tid not in result[uid]:
                    result[uid][tid] = []
                result[uid][tid].append(err)
            else:
                result[uid] = {tid: [err]}

        for uid in result:
            for tid in result[uid]:
                codes = result[uid][tid]
                if codes.count(0) > 0:
                    result[uid][tid] = 'solved'
                else:
                    result[uid][tid] = 'error'

        return result

    def get(self, request, format=None):
        """Список решений пользователей
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        found_users = serializer.validated_data['found_users']
        found_tasks = serializer.validated_data['found_tasks']
        summary = serializer.validated_data['summary']
        limit = serializer.validated_data['limit']

        solutions = Solution.fetch_solutions(found_tasks, found_users, limit)

        result = {
            'tasks': serialize(
                serializers.TaskSimpleSerializer,
                found_tasks,
                many=True).data,
            'users': serialize(
                serializers.UserSerializer,
                found_users,
                many=True).data
        }

        if summary:
            result['summary'] = self.create_solutions_summary(solutions)
        else:
            result['solutions'] = serialize(
                serializers.SolutionsListSerializer,
                solutions,
                many=True).data

        return Response(result)


class UserPageView(APIView):

    def get(self, request, username, format=None):
        """Данные пользователя
        """
        try:
            user = User.objects.get(username=username)
            profile = Profile.get_user_profile(user)
        except User.DoesNotExist:
            raise NotFound()

        user_serializer = serialize(serializers.UserSerializer, user)
        profile_serializer = serialize(serializers.ProfileSerializer, profile)

        data = user_serializer.data
        data.update(profile_serializer.data)

        return Response(data)


class UsersView(APIView):

    def get(self, request, format=None):
        """Список пользователей для преподавателя
        """
        if request.user.is_staff:
            users = User.objects.filter(is_staff=False).order_by('id')
            serializer = serialize(serializers.UserSerializer, users, many=True)
            users_data = serializer.data

            return Response(users_data)
        else:
            raise PermissionDenied()


class IMView(APIView):

    def _get_notification_ids(self, serialized_messages):

        ids = []
        for message in serialized_messages['messages']:
            if message['notification_id'] is not None:
                ids.append(message['notification_id'])

        return ids

    def get(self, request, format=None):
        """Получение сообщений для каждого пользователя
        """
        messages = get_user_messages(request.user.id)

        if messages is not None:
            serializer = serialize(serializers.IMSerializer, messages)
            Notification.mark_seen(self._get_notification_ids(serializer.data))

            return Response(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsView(APIView):

    def get(self, request, format=None):
        """Получение комментариев пользователя под
            определенным заданием
        """
        data = deserialize(
            serializers.CommentsListParamsSerializer,
            request.query_params
        ).data

        if request.user.username != data['username']:
            if not request.user.is_staff:
                raise PermissionDenied()

            try:
                user = User.objects.get(username=data['username'])
            except User.DoesNotExist:
                raise NotFound()
        else:
            user = request.user

        comments = Comment.objects.filter(
            task__id=data['task_id'],
            task_owner=user
        ).order_by('-id')

        serializer = serialize(serializers.CommentSerializer, comments, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        """Публикация комментария под заданием пользователя
        """
        serializer = deserialize(serializers.CommentSerializer, data=request.data)

        if request.user.username != serializer.validated_data['username']:
            if not request.user.is_staff:
                raise PermissionDenied()

        comment = serializer.save(user=request.user)

        recipients = get_staff(exclude=[request.user, comment.task_owner])

        if request.user.id != comment.task_owner.id:
            recipients.append(comment.task_owner)

        # Формирование нотификации
        #
        name_inflected = inflect_name(
            serializer.data['user']['first_name'],
            serializer.data['user']['last_name'])
        msg = '<a href="/tasks/{task_id}?username={comment_username}">Новый комментарий</a>' \
            + ' от <a href="/users/{commenter_username}">{commenter}</a> в задании #{task_id}'
        alert_msg = msg.format(
            task_id=comment.task.id,
            comment_username=serializer.validated_data['username'],
            commenter_username=serializer.data['user']['username'],
            commenter=name_inflected)

        Notification.send_many(
            recipients,
            request.user,
            'co',
            html=alert_msg,
            im_payload=serializer.data)

        return Response(serializer.data)


class CommentView(APIView):

    def delete(self, request, comment_id, format=None):
        """Удаление определенного комментария
        """
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise NotFound()

        if comment.user.id != request.user.id:
            raise PermissionDenied()

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TestsGenerateView(APIView):

    def post(self, request, format=None):
        """Генерация тестов с помощью скрипта
        """
        if not request.user.is_staff:
            raise PermissionDenied()

        serializer_in = deserialize(
            serializers.TestsGenerateSerializer, request.data)

        script_path = Task.save_test_generator(
            serializer_in.validated_data['source'],
            Task.get_test_generator_path(request.user)
        )

        django_rq.enqueue(generate_tests, script_path, request.user.id)

        return Response(status=status.HTTP_200_OK)


class TestsCheckerView(APIView):

    def post(self, request):
        """Проверка чекера тестов
        """
        if not request.user.is_staff:
            raise PermissionDenied()

        serializer_in = deserialize(
            serializers.TestsGenerateSerializer, request.data)

        script_path = Task.save_test_checker(
            serializer_in.validated_data['source'],
            Task.get_test_checker_path(request.user)
        )

        django_rq.enqueue(load_and_check_module, script_path, request.user.id)

        return Response(status=status.HTTP_200_OK)


class DashboardViews(APIView):

    def _all_users_all_tasks(self, task_ids):

        user_ids = User.objects.filter(
            is_staff=False).order_by('id').values_list('id', flat=True)

        return {
            'user_ids': user_ids,
            'task_ids': task_ids
        }

    def _online_users_all_tasks(self, task_ids):

        user_ids = [u.id for u in Profile.get_online_users()]

        return {
            'user_ids': user_ids,
            'task_ids': task_ids
        }

    def _week_users_all_tasks(self, task_ids):

        week_delta = timedelta(days=7)
        user_ids = [u.id for u in Profile.get_active_users(week_delta)]

        return {
            'user_ids': user_ids,
            'task_ids': task_ids
        }

    def _failed_tasks(self):

        user_ids, task_ids = Solution.fetch_failed_with_users()

        return {
            'user_ids': user_ids,
            'task_ids': task_ids
        }

    def get(self, request):
        """Получение аггрегированных данных для dashboard
        """
        all_tasks_ids = Task.objects.all().order_by('id').values_list('id', flat=True)

        result = {
            'all_users_all_tasks': self._all_users_all_tasks(all_tasks_ids),
            'online_users_all_tasks': self._online_users_all_tasks(all_tasks_ids),
            'week_users_all_tasks': self._week_users_all_tasks(all_tasks_ids),
            'failed_tasks': self._failed_tasks()
        }

        return Response(result)


class NotificationsCountView(APIView):

    def get(self, request):
        """Возвращает количество непрочитанных нотификаций
        """
        count = Notification.objects.filter(
            user_for=request.user, seen=False).count()

        return Response({
            'count': count
        })


class NotificationsView(generics.ListAPIView):

    serializer_class = serializers.NotificationsSerializer

    def get_queryset(self):

        user = self.request.user
        return Notification.objects.filter(user_for=user).order_by('-id')
