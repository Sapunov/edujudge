from rest_framework import serializers

from judge.api.models import Task, Test, Example, Solution


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

    def create(self, validated_data):

        notes = validated_data.get('notes')

        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            initial_data=validated_data['initial_data'],
            result=validated_data['result'],
            timelimit=validated_data['timelimit'],
            author=validated_data['user'],
            notes=notes if notes else None
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


class SolutionsListSerializer(serializers.Serializer):

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