import re
import logging
from subprocess import PIPE, Popen, TimeoutExpired

from django.conf import settings

from judge.api.models import Solution
from judge.api.im import send_message
from judge.api.common import get_staff_ids

log = logging.getLogger('main.' + __name__)


def mask_output(output):

    return re.sub(r'"' + settings.SOURCE_DIR + r'.*"', 'solution.py', output)


def interpreter_test(solution_path, input, timelimit):

    error_code = 0
    output = None
    out = err = b''

    bytes_input = bytes(input, 'utf-8')

    proc = Popen(
        ['python3', solution_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    try:
        out, err = proc.communicate(input=bytes_input, timeout=timelimit)

        if err:
            error_code = 1

    except TimeoutExpired:
        error_code = 3

    output = out.decode() if error_code == 0 else err.decode()
    output = mask_output(output)

    return (error_code, output)


def match_solutions(output, right):

    output = output.strip()
    right = right.strip()

    output_lines, right_lines = output.split('\n'), right.split('\n')

    if len(output_lines) != len(right_lines):
        return False

    for i in range(len(right_lines)):
        output_line = output_lines[i].strip()
        right_line = right_lines[i].strip()

        if output_line != right_line:
            return False

    return True


def test_solution(solution_id):

    solution = Solution.objects.get(pk=solution_id)

    timelimit = solution.task.timelimit

    for i, test in enumerate(solution.task.tests.order_by('id')):
        error_code, output = interpreter_test(
            solution.source_path,
            test.text,
            timelimit
        )

        if error_code != 0 or not match_solutions(output, test.answer):
            solution.test = test
            solution.testnum = i + 1

            if error_code != 0:
                solution.error = error_code
                solution.verdict = output
            else:
                solution.error = 2

            break
    else:
        solution.verdict = 'ok'

    solution.save()

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
        'test': test_input
    }

    verdict = 'Все правильно!' if solution.error == 0 else 'Есть ошибки :=('

    send_message(
        user_id=solution.user.id,
        msg_type='test_complete',
        message=msg,
        alert_msg='Задание {0} проверено. {1}'.format(solution.task.id, verdict)
    )

    # Сообщение для преподавателей, которое обновит /students
    staff = get_staff_ids(exclude=[solution.user.id])
    log.debug('Sending `students_did` msg to %s' % staff)
    send_message(
        user_id=staff,
        msg_type='students_did',
        message={}
    )
