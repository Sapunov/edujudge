import sys
import os.path
from importlib import import_module

from judge.api.models import Task
from judge.api import serializers
from judge.api import im


class ResultItem:

    def __init__(self, text, answer):

        self.text = text
        self.answer = answer

class Result:

    def __init__(self, path, items):

        self.test_generator = path
        self.tests = items


def check_module(module):

    attrs = ['NUMBER_OF_TESTS', 'generate']

    for attr in attrs:
        if not hasattr(module, attr):
            return 'The module does not have an attribute: {0}'.format(attr)

    if getattr(module, 'NUMBER_OF_TESTS') < 1:
        return 'The number of tests is zero'

    try:
        result = getattr(module, 'generate')()
    except Exception as e:
        return str(e)

    if not isinstance(result, tuple):
        return 'Type of return value must be <tuple> not <{0}>'.format(type(result))

    if len(result) != 2:
        return 'Number of return elements must be 2'

    if not all([isinstance(it, str) for it in result]):
        return 'Type of each return element must be <str>'


def _generate_tests(path_to_script):

    module_path, script = path_to_script.rsplit('/', 1)
    module_name, _ = os.path.splitext(script)

    is_error = False
    error_msg = ''

    if module_path not in sys.path:
        sys.path.append(module_path)

    try:
        module = import_module(module_name)
    except Exception as e:
        return ( False, str(e) )

    checked = check_module(module)

    if checked is not None:
        return ( False, checked )

    results = []

    for i in range(getattr(module, 'NUMBER_OF_TESTS')):
        try:
            results.append(
                ResultItem(
                    *getattr(module, 'generate')()
                )
            )
        except Exception as e:
            return ( False, 'Exception while generate {0} test: {1}'.format(i + 1, e) )

    return ( True, Result(script, results) )


def generate_tests(path_to_script, user_id):

    is_ok, result = _generate_tests(path_to_script)

    if not is_ok:
        Task.remove_test_generator(path_to_script)

        im.send_message(
            user_id=user_id,
            msg_type='error_testgenerating',
            message=result,
            alert_msg='Во время генерации тестов произошла ошибка'
        )
    else:
        serializer = serializers.serialize(
            serializers.TestGenResultsSerializer, result)

        im.send_message(
            user_id=user_id,
            msg_type='ok_testgenerating',
            message=serializer.data,
            alert_msg='Генерация тестов завершена успешно'
        )
