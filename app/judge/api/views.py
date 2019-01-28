import django_rq
import logging

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from judge.api import im
from judge.api import serializers
from judge.api.common import inflect_name, get_staff_ids, get_logger
from judge.api.common import list_to_dict
from judge.api.im import get_user_messages
from judge.api.models import Task, Solution, Comment, Profile
from judge.api.serializers import serialize, deserialize
from judge.api.testcheckers import load_and_check_module
from judge.api.testgenerators import generate_tests
from judge.api.testsystem import test_solution


log = logging.getLogger('main.' + __name__)


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

        try:
            user = User.objects.get(username=username)
            profile = Profile.get_user_profile(user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_serializer = serialize(serializers.UserSerializer, user)
        profile_serializer = serialize(serializers.ProfileSerializer, profile)

        data = user_serializer.data
        data.update(profile_serializer.data)

        return Response(data)


class UsersView(APIView):

    def get(self, request, format=None):

        if request.user.is_staff:
            users = User.objects.filter(is_staff=False).order_by('id')
            serializer = serialize(serializers.UserSerializer, users, many=True)
            users_data = serializer.data

            return Response(users_data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


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
            name_inflected = inflect_name(
                serializer.data['user']['first_name'],
                serializer.data['user']['last_name'])
            msg = '<a href="/tasks/{task_id}?username={comment_username}">Новый комментарий</a>' \
                + ' от <a href="/users/{commenter_username}">{commenter}</a> в задании #{task_id}'
            im.send_message(
                user_id=users,
                msg_type='new_comment',
                message=serializer.data,
                alert_msg=msg.format(
                    task_id=comment.task.id,
                    comment_username=serializer.validated_data['username'],
                    commenter_username=serializer.data['user']['username'],
                    commenter=name_inflected
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


class TestsCheckerView(APIView):

    def post(self, request):

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer_in = deserialize(
            serializers.TestsGenerateSerializer, request.data)

        script_path = Task.save_test_checker(
            serializer_in.validated_data['source'],
            Task.get_test_checker_path(request.user)
        )

        django_rq.enqueue(load_and_check_module, script_path, request.user.id)

        return Response(status=status.HTTP_200_OK)


class DashboardViews(APIView):

    def _all_users_all_tasks(self):

        users = User.objects.filter(is_staff=False).order_by('id').values_list('id', flat=True)
        tasks = Task.objects.all().order_by('id').values_list('id', flat=True)

        return {
            'user_ids': users,
            'task_ids': tasks
        }

    def get(self, request):

        result = {
            'all_users_all_tasks': self._all_users_all_tasks()
        }

        return Response(result)
