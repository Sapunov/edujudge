import os
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound

from judge.api.models import Task, Test, Example, Solution, Comment


def deserialize(serializer_class, data):

    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)

    return serializer


def serialize(serializer_class, instance, data=None, **kwargs):

    if data is None:
        serializer = serializer_class(instance, **kwargs)
    else:
        serializer = serializer_class(instance, data=data, **kwargs)
        serializer.is_valid(raise_exception=True)

    return serializer


class TaskTestSerializer(serializers.Serializer):

    text = serializers.CharField()
    answer = serializers.CharField()


class TaskExampleSerializer(serializers.Serializer):

    text = serializers.CharField()
    answer = serializers.CharField()


class TaskSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    initial_data = serializers.CharField()
    result = serializers.CharField()
    examples = TaskExampleSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    timelimit = serializers.IntegerField()
    tests = TaskTestSerializer(many=True)
    test_generator_path = serializers.CharField(allow_null=True)

    def create(self, validated_data):

        notes = validated_data.get('notes')
        generator_path = validated_data.get('test_generator_path')

        if generator_path is not None:
            generator_path = os.path.join(settings.TEST_GENERATORS_DIR, generator_path)

        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            initial_data=validated_data['initial_data'],
            result=validated_data['result'],
            timelimit=validated_data['timelimit'],
            author=validated_data['user'],
            notes=notes if notes else None,
            test_generator_path=generator_path
        )

        for testitem in validated_data['tests']:
            test = Test.objects.create(
                task=task,
                text=testitem['text'],
                answer=testitem['answer']
            )

        for exampleitem in validated_data['examples']:
            example = Example.objects.create(
                task=task,
                text=exampleitem['text'],
                answer=exampleitem['answer']
            )

        return task


class TasksListSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=100)
    solved = serializers.IntegerField()


class TaskCheckSerializer(serializers.Serializer):

    source = serializers.CharField()


    def create(self, validated_data):

        solution = Solution.create(
            task=validated_data.get('task'),
            source=validated_data.get('source'),
            user=validated_data.get('user')
        )

        return solution


class SolutionsListParamsSerializer(serializers.Serializer):

    task_id = serializers.IntegerField()
    username = serializers.CharField()


class CommentsListParamsSerializer(serializers.Serializer):

    task_id = serializers.IntegerField()
    username = serializers.CharField()


class UserInParamsSerializer(serializers.Serializer):

    user = serializers.CharField(required=False)


class SolutionsListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    task_id = serializers.PrimaryKeyRelatedField(read_only=True)
    test = serializers.SlugRelatedField(slug_field='text', read_only=True)
    testnum = serializers.IntegerField()
    time = serializers.DateTimeField(format='%m-%d-%Y %H:%M:%S')
    error = serializers.IntegerField()
    verdict = serializers.CharField()
    error_description = serializers.CharField()
    source = serializers.CharField()


class TaskOnlySerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    initial_data = serializers.CharField()
    result = serializers.CharField()
    examples = TaskExampleSerializer(many=True)
    notes = serializers.CharField()
    timelimit = serializers.IntegerField()
    solved = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_staff')


class IMMessagesSerializer(serializers.Serializer):

    msg_type = serializers.CharField()
    alert_msg = serializers.CharField(allow_null=True)
    payload = serializers.JSONField()


class IMSerializer(serializers.Serializer):

    count_messages = serializers.IntegerField()
    messages = IMMessagesSerializer(many=True)


class CommentSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    user = UserSerializer(required=False)
    time = serializers.DateTimeField(format='%m-%d-%Y %H:%M:%S', required=False)
    text = serializers.CharField()
    task_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)
    task_owner = UserSerializer(required=False)

    def create(self, validated_data):

        if 'task_id' not in validated_data:
            raise ValidationError({'task_id': ['This field is required.']})

        if 'username' not in validated_data:
            raise ValidationError({'username': ['This field is required.']})

        try:
            task = Task.objects.get(pk=validated_data['task_id'])
        except Task.DoesNotExist:
            raise NotFound

        try:
            owner = User.objects.get(username=validated_data['username'])
        except User.DoesNotExist:
            raise NotFound

        comment = Comment.objects.create(
            task=task,
            user=validated_data['user'],
            text=validated_data['text'],
            task_owner=owner
        )

        return comment


class TestsGenerateSerializer(serializers.Serializer):

    source = serializers.CharField()


class TestGenResultsItemSerializer(serializers.Serializer):

    text = serializers.CharField()
    answer = serializers.CharField()


class TestGenResultsSerializer(serializers.Serializer):

    test_generator = serializers.CharField(allow_null=True)
    tests = TestGenResultsItemSerializer(many=True)
