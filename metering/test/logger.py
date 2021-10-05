import unittest
import logging
from metering.logger import Logger
from metering.test.logging_test_handler import TestHandler, Matcher

MESSAGE = 'my message'
MESSAGE_WITH_ARGUMENT = 'error uploading: %s'
AMBERFLO_LOGGER = 'amberflo'

class TestLogger(unittest.TestCase):
    """Test class for Logger"""

    def setUp(self):
        self.handler = TestHandler(Matcher())
        self.pythonLogger = logging.getLogger()
        self.pythonLogger.addHandler(self.handler)
        
    def tearDown(self):
        self.pythonLogger.removeHandler(self.handler)
        self.handler.close()

    # def test_debug(self):
    #     amberflo_log = Logger()
    #     amberflo_log.debugMode()
    #     amberflo_log.debug(MESSAGE)

    #     handler = self.handler
    #     self.assertTrue(handler.matches(levelno=logging.DEBUG))
    #     self.assertTrue(handler.matches(msg=MESSAGE))


    def test_warn(self):
        amberflo_log = Logger()
        amberflo_log.warn(MESSAGE)

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.WARNING))
        self.assertTrue(handler.matches(msg=MESSAGE))


    def test_error(self):
        amberflo_log = Logger()
        amberflo_log.error(MESSAGE)

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.ERROR))
        self.assertTrue(handler.matches(msg=MESSAGE))


    # def test_debug_with_arguments(self):
    #     amberflo_log = Logger()
    #     amberflo_log.debug(MESSAGE_WITH_ARGUMENT, '1')

    #     handler = self.handler
    #     self.assertTrue(handler.matches(levelno=logging.DEBUG))
    #     self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))


    def test_warn_with_arguments(self):
        amberflo_log = Logger()
        amberflo_log.warn(MESSAGE_WITH_ARGUMENT, '1')

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.WARN))
        self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))


    def test_error_with_arguments(self):
        amberflo_log = Logger()
        amberflo_log.error(MESSAGE_WITH_ARGUMENT, '1')

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.ERROR))
        self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))

    def test_debug_with_arguments_throws_exception(self):
        amberflo_log = Logger()
        amberflo_log.debugMode()

        # no exception
        amberflo_log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')


    def test_warn_with_arguments_throws_exception(self):
        amberflo_log = Logger()

        # no exception
        amberflo_log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')


    def test_error_with_arguments_throws_exception(self):
        amberflo_log = Logger()

        # no exception
        amberflo_log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')

if __name__ == '__main__':
    unittest.main()
