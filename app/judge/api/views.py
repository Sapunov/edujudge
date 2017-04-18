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
from judge.api.models import Task, Solution


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

        solutions = Solution.get_by_task_user(data['task_id'], request.user)

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
            serializer = serialize(serializers.UserSerializer, users, many=True)

            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class IMView(APIView):

    def get(self, request, format=None):

        messages = get_user_messages(request.user.id)

        if messages is not None:
            serializer = serialize(serializers.IMSerializer, messages)

            return Response(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)
