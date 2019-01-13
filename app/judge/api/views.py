import django_rq

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from judge.api import serializers
from judge.api.serializers import serialize, deserialize
from judge.api.testsystem import test_solution
from judge.api.im import get_user_messages
from judge.api.models import Task, Solution, Comment
from judge.api import im
from judge.api.common import word_gent, get_staff_ids, get_logger
from judge.api.testgenerators import generate_tests

log = get_logger(__name__)


class TasksListView(APIView):

    def get(self, request, format=None):

        data = deserialize(
            serializers.UserInParamsSerializer,
            request.query_params
        ).data

        if 'user' in data:
            try:
                user = User.objects.get(username=data['user'])
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        tasks = Task.all_with_user_solution(user)
        serializer = serialize(serializers.TasksListSerializer, tasks, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = deserialize(serializers.TaskSerializer, data=request.data)
        serializer.save(user=request.user)

        return Response(status=status.HTTP_200_OK)


class TaskView(APIView):

    def get(self, request, task_id, format=None):

        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        task.solved = Solution.is_task_solved(task_id, request.user)

        serializer = serialize(serializers.TaskOnlySerializer, task)

        return Response(serializer.data)


class TaskCheckView(APIView):

    def post(self, request, task_id, format=None):

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


class SolutionsListView(APIView):

    def get(self, request, format=None):

        data = deserialize(
            serializers.SolutionsListParamsSerializer,
            request.query_params
        ).data

        if request.user.username != data['username']:
            if not request.user.is_staff:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                user = User.objects.get(username=data['username'])
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        solutions = Solution.get_by_task_user(data['task_id'], user)

        serializer = serialize(
            serializers.SolutionsListSerializer, solutions, many=True)

        return Response(serializer.data)


class UserPageView(APIView):

    def get(self, request, username, format=None):

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serialize(serializers.UserSerializer, user)

        return Response(serializer.data)


class UsersView(APIView):

    def get(self, request, format=None):

        if request.user.is_staff:
            users = User.objects.filter(is_staff=False)
            for user in users:
                user_tasks = Task.all_with_user_solution(user)
                tasks_solved = len([_ for _ in user_tasks if _.solved == 1])
                tasks_failed = len([_ for _ in user_tasks if _.solved == 0])
                tasks_untouched = len([_ for _ in user_tasks if _.solved == -1])
                #
                setattr(user, 'tasks_solved', tasks_solved)
                setattr(user, 'tasks_failed', tasks_failed)
                setattr(user, 'tasks_untouched', tasks_untouched)

            serializer = serialize(serializers.UserSerializer, users, many=True)
            users_data = serializer.data

            return Response(users_data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class IMView(APIView):

    def get(self, request, format=None):

        messages = get_user_messages(request.user.id)

        if messages is not None:
            serializer = serialize(serializers.IMSerializer, messages)

            return Response(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsView(APIView):

    def get(self, request, format=None):

        data = deserialize(
            serializers.CommentsListParamsSerializer,
            request.query_params
        ).data

        if request.user.username != data['username']:
            if not request.user.is_staff:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                user = User.objects.get(username=data['username'])
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        comments = Comment.objects.filter(
            task__id=data['task_id'],
            task_owner=user
        ).order_by('-id')

        serializer = serialize(serializers.CommentSerializer, comments, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = deserialize(serializers.CommentSerializer, data=request.data)

        if request.user.username != serializer.validated_data['username']:
            if not request.user.is_staff:
                return Response(status=status.HTTP_403_FORBIDDEN)

        comment = serializer.save(user=request.user)

        users = get_staff_ids(
            exclude=[request.user.id, comment.task_owner.id]
        )

        if request.user.id != comment.task_owner.id:
            users.append(comment.task_owner.id)

        try:
            im.send_message(
                user_id=users,
                msg_type='new_comment',
                message=serializer.data,
                alert_msg='Новый комментарий от {0} {1} в задании {2}'.format(
                    word_gent(serializer.data['user']['first_name']),
                    word_gent(serializer.data['user']['last_name']),
                    comment.task.id
                )
            )
        except Exception as exc:
            log.exception(exc)

        return Response(serializer.data)


class CommentView(APIView):

    def delete(self, request, comment_id, format=None):

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if comment.user.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TestsGenerateView(APIView):

    def post(self, request, format=None):

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer_in = deserialize(
            serializers.TestsGenerateSerializer, request.data)

        script_path = Task.save_test_generator(
            serializer_in.validated_data['source'],
            Task.get_test_generator_path(request.user)
        )

        django_rq.enqueue(generate_tests, script_path, request.user.id)

        return Response(status=status.HTTP_200_OK)
