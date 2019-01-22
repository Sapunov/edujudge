import sys
import os.path
from importlib import import_module
import logging

from judge.api.models import Task
from judge.api import im

log = logging.getLogger('main.' + __name__)


def check_module(module):

    attrs = ['check_test']

    for attr in attrs:
        if not hasattr(module, attr):
            return 'The module does not have an attribute: {0}'.format(attr)

    EMPTY_STRING = ''

    try:
        result = getattr(module, 'check_test')(EMPTY_STRING, EMPTY_STRING, EMPTY_STRING)
    except Exception as e:
        return str(e)

    if not isinstance(result, bool):
        return 'Type of return value must be <bool> not <{0}>'.format(type(result))

    return None


def load_module(path_to_script, check):

    module_path, script = path_to_script.rsplit('/', 1)
    module_name, _ = os.path.splitext(script)

    if module_path not in sys.path:
        sys.path.append(module_path)

    try:
        module = import_module(module_name)
    except Exception as e:
        return ( False, str(e), script )

    if check:
        checked = check_module(module)

        if checked is not None:
            return ( False, checked, script )

    return ( True, module, script )


def load_and_check_module(path_to_script, user_id, check=True):

    ok, module_or_error, script_name = load_module(path_to_script, check)

    if ok:
        im.send_message(
            user_id=user_id,
            msg_type='ok_testchecker',
            message={'test_checker': script_name},
            alert_msg='Чекер сохранен'
        )
    else:
        Task.remove_test_checker(path_to_script)

        im.send_message(
            user_id=user_id,
            msg_type='error_testchecker',
            message=module_or_error,
            alert_msg='Во время сохранения чекера произошла ошибка')


def run_checker(test_input, test_output, user_output, checker_path):

    ok, module_or_error, script_name = load_module(checker_path, check=False)

    if ok:
        try:
            return getattr(module_or_error, 'check_test')(
                test_input, test_output, user_output)
        except ValueError as program_error:
            log.info('Checker raise ValueError: %s' % program_error)
            return False
        except Exception as e:
            log.error('Exception while running checker. ' \
                'test_input=%s, test_output=%s, user_output=%s, ' \
                'checker_path=%s' % (test_input, test_output, user_output, checker_path))
            log.excption(e)
            return False
    else:
        log.error('Error while loading and checking checker: %s' % module_or_error)

    return False
