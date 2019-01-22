import re
import logging
from subprocess import PIPE, Popen, TimeoutExpired

from django.conf import settings

from judge.api import constants
from judge.api import exceptions
from judge.api.common import get_staff_ids
from judge.api.im import send_message
from judge.api.models import Solution
from judge.api.testcheckers import run_checker

log = logging.getLogger('main.' + __name__)


def mask_output(output):
    '''Замена реального пути к файлу с кодом на стандартный.'''

    return re.sub(r'"' + settings.SOURCE_DIR + r'.*"', 'solution.py', output)


def fetch_line(output):
    '''Возвращает строку на которой произошла ошибка
    '''

    lines = output.split('\n')
    target_line = None
    for i, line in enumerate(lines):
        if 'solution.py' in line:
            target_line = i
            break

    if target_line is not None:
        match = re.search('line ([0-9]+)', lines[target_line])
        if match:
            num = int(match.group(1))
            return num

    return -1


def interpreter_test(solution_path, input_text, timelimit):
    '''Тест интерпретатором с входными данными
    '''
    output = None
    s_out = s_err = b''

    bytes_input = bytes(input_text, 'utf-8')

    proc = Popen(
        ['python3', solution_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    try:
        s_out, s_err = proc.communicate(input=bytes_input, timeout=timelimit)

        if s_err:
            error_out = s_err.decode()
            raise exceptions.TestCompilingError(msg=error_out)
    except TimeoutExpired:
        raise exceptions.TimeLimitExceededException()

    output = mask_output(s_out.decode())

    return output


def match_solution_by_lines(output, right):
    '''Простое построчное сравнение ответа программы студента
        с эталонным ответом на тест.
    '''

    output = output.strip()
    right = right.strip()

    output_lines, right_lines = output.split('\n'), right.split('\n')

    if len(output_lines) != len(right_lines):
        raise exceptions.TestWrongAnswer()

    for i, right_line in enumerate(right_lines):
        output_line = output_lines[i].strip()
        right_line = right_line.strip()

        if output_line != right_line:
            raise exceptions.TestWrongAnswer()


def match_solution_with_checker(test_input, test_output, user_output, checker_path):

    if not run_checker(test_input, test_output, user_output, checker_path):
        raise exceptions.TestWrongAnswer()


def notify_about_solution(solution):

    if solution.test is not None:
        test_input = solution.test.text
        if len(test_input) > settings.TEST_INPUT_MAX_LEN:
            test_input = test_input[:settings.TEST_INPUT_MAX_LEN]
            test_input += ' <данные обрезаны из-за большого размера>'
    else:
        test_input = None

    msg = {
        'error': solution.error,
        'error_description': settings.TEST_ERRORS[solution.error],
        'verdict': solution.verdict,
        'testnum': solution.testnum,
        'task_id': solution.task.id,
        'test': test_input,
        'error_line': solution.error_line
    }

    alert_verdict = 'Все правильно!' if solution.error == constants.TEST_OK \
        else 'Есть ошибки :=('

    send_message(
        user_id=solution.user.id,
        msg_type='test_complete',
        message=msg,
        alert_msg='<a href="/tasks/{0}">Задание #{0}</a> проверено. {1}'.format(
            solution.task.id, alert_verdict)
    )

    # Сообщение для преподавателей, которое обновит /dashboard
    staff = get_staff_ids(exclude=[solution.user.id])
    send_message(
        user_id=staff,
        msg_type='students_did',
        message=None
    )


def test_solution(solution_id):

    solution = Solution.objects.get(pk=solution_id)
    timelimit = solution.task.timelimit

    log.debug('Start testing %s with timelimit=%s seconds' % (solution, timelimit))

    for i, test in enumerate(solution.task.tests.order_by('id')):
        try:
            output = interpreter_test(
                solution.source_path,
                test.text,
                timelimit)
            if solution.task.has_checker:
                log.debug('Check %s with checker: %s' % (
                    solution, solution.task.test_checker_path))
                match_solution_with_checker(
                    test.text,
                    test.answer,
                    output,
                    solution.task.test_checker_path)
            else:
                log.debug('Match %s with simple string checker' % solution)
                match_solution_by_lines(output, test.answer)
        except exceptions.TestException as exc:
            log.debug('Get exception: %s on %s for %s' % (exc.name, test, solution))
            solution.test = test
            solution.testnum = i + 1

            if isinstance(exc, exceptions.TimeLimitExceededException):
                solution.error = constants.TEST_TIME_LIMIT_EXCEEDED
            elif isinstance(exc, exceptions.TestCompilingError):
                solution.error = constants.TEST_COMPILING_ERROR
                solution.verdict = mask_output(exc.msg)
                solution.error_line = fetch_line(solution.verdict)
            elif isinstance(exc, exceptions.TestWrongAnswer):
                solution.error = constants.TEST_WRONG_ANSWER

            break
    else:  # Ни разу не был выполнен break
        solution.verdict = 'ok'

    solution.save()
    notify_about_solution(solution)
