from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import django_rq
from judge.api import serializers
from judge.api.serializers import serialize, deserialize
from judge.api.testsystem import test_solution


from judge.api.models import Task


class TasksListView(APIView):

    def get(self, request, format=None):

        tasks = Task.objects.all()
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

        job = django_rq.enqueue(test_solution, solution_id=solution.id)

        return Response({ 'qid': job.id })


class QueueView(APIView):

    def get(self, request, qid, format=None):

        default_queue = django_rq.get_queue('default')
        job = default_queue.fetch_job(qid)

        return Response({
            'qid': qid,
            'status': job.status,
            'finished': job.is_finished,
            'result': job.result
        })
