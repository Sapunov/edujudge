import os
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from judge.api.models import Task, Test, Example, Solution, Comment
from judge.api.common import count_data_types


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


class TaskSimpleSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.CharField()


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

    tasks_ids = serializers.CharField()
    usernames_or_ids = serializers.CharField()
    summary = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(default=5)

    def check_and_get_users(self, usernames_or_ids):

        if len(usernames_or_ids) == 0:
            raise ValidationError({
                'usernames_or_ids': [
                    'You need to specify at least one user']})

        for i, uid in enumerate(usernames_or_ids):
            if str.isdigit(uid):
                usernames_or_ids[i] = int(uid)

        data_types = count_data_types(usernames_or_ids)

        if len(data_types) > 1:
            raise ValidationError({
                'usernames_or_ids': [
                    'You need to pass either the ids or usernames']})

        if len(data_types.keys() - set(('str', 'int'))) > 0:
            raise ValidationError({
                'usernames_or_ids': [
                    'Allowed types of identifiers: int, str']})

        if isinstance(usernames_or_ids[0], str):
            found_users = User.objects.filter(username__in=usernames_or_ids)
        else:
            found_users = User.objects.filter(pk__in=usernames_or_ids)

        found_users = found_users.order_by('first_name', 'last_name')

        if len(found_users) != len(usernames_or_ids):
            raise NotFound({'usernames_or_ids': ['Not all users found']})

        return found_users

    def check_and_get_tasks(self, tasks_ids):

        if len(tasks_ids) == 0:
            raise ValidationError({
                'tasks_ids': [
                    'You need to specify at least one task_id']})

        tasks = Task.objects.filter(pk__in=tasks_ids).order_by('id')

        if len(tasks) != len(tasks_ids):
            raise NotFound({'tasks_ids': ['Not all tasks found']})

        return tasks

    def validate(self, attrs):

        user = self.context['request'].user
        tasks_ids = attrs['tasks_ids'].split(',')
        usernames_or_ids = attrs['usernames_or_ids'].split(',')

        found_users = self.check_and_get_users(usernames_or_ids)
        found_users_ids = [user.id for user in found_users]

        # Проверка на то, что пользователю можно показать
        # эти решения
        if len(set(found_users_ids) - set([user.id])) > 0 and not user.is_staff:
            raise PermissionDenied()

        found_tasks = self.check_and_get_tasks(tasks_ids)

        attrs['found_users'] = found_users
        attrs['found_tasks'] = found_tasks

        return attrs


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
    time = serializers.DateTimeField(format=settings.UI_DATETIME_FORMAT)
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
    time = serializers.DateTimeField(format=settings.UI_DATETIME_FORMAT, required=False)
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
            raise NotFound({'task_id': ['Task with the specified id does not exist']})

        try:
            owner = User.objects.get(username=validated_data['username'])
        except User.DoesNotExist:
            raise NotFound({'username': ['User with the specified username does not exist']})

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
