import logging
from subprocess import PIPE, Popen, TimeoutExpired
from judge.api.models import Solution

log = logging.getLogger('main.' + __name__)


def interpreter_test(solution_path, input, timelimit):

    error_code = 0
    output = None
    out = err = b''

    bytes_input = bytes(input, 'utf-8')

    proc = Popen(
        ['python', solution_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    try:
        out, err = proc.communicate(input=bytes_input, timeout=timelimit)

        if err:
            error_code = 1

    except TimeoutExpired:
        error_code = 3

    output = out.decode() if error_code == 0 else err.decode()

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

        log.debug('error_code: %s, output: %s', error_code, output)

        if error_code != 0 or not match_solutions(output, test.answer):
            solution.test = test
            solution.testnum = i + 1

            if error_code != 0:
                solution.error = error_code
                solution.verdict = output
            else:
                solution.error = 2

            solution.save()
            break
    else:
        solution.verdict = 'ok'
        solution.save()

    return {
        'error_code': error_code,
        'verdict': solution.verdict,
        'testnum': solution.testnum,
        'task_id': solution.task.id
    }
