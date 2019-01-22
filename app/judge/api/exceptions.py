class JudgeException(Exception):

    default_msg = 'Judge exception occurs'

    def __init__(self, msg=None):

        if msg is None:
            self.msg = self.default_msg

    def __str__(self):

        return self.msg

    @property
    def name(self):

        return self.__class__.__name__


class TestException(JudgeException):

    pass



class TimeLimitExceededException(TestException):

    default_msg = 'The test time exceeded the expected value'

    def __init__(self, msg=None):

        if msg is None:
            self.msg = self.default_msg


class TestCompilingError(TestException):

    def __init__(self, msg):

        self.msg = msg


class TestWrongAnswer(TestException):

    pass
