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
        self.logger = logging.getLogger()
        self.logger.addHandler(self.handler)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()

    def test_debug(self):
        log = Logger()
        log.debugMode()
        log.debug(MESSAGE)

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.DEBUG))
        self.assertTrue(handler.matches(msg=MESSAGE))


    def test_warn(self):
        log = Logger()
        log.warn(MESSAGE)

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.WARNING))
        self.assertTrue(handler.matches(msg=MESSAGE))


    def test_error(self):
        log = Logger()
        log.error(MESSAGE)

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.ERROR))
        self.assertTrue(handler.matches(msg=MESSAGE))


    def test_debug_with_arguments(self):
        log = Logger()
        log.debugMode()
        log.debug(MESSAGE_WITH_ARGUMENT, '1')

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.DEBUG))
        self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))


    def test_warn_with_arguments(self):
        log = Logger()
        log.warn(MESSAGE_WITH_ARGUMENT, '1')

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.WARN))
        self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))


    def test_error_with_arguments(self):
        log = Logger()
        log.error(MESSAGE_WITH_ARGUMENT, '1')

        handler = self.handler
        self.assertTrue(handler.matches(levelno=logging.ERROR))
        self.assertTrue(handler.matches(msg=MESSAGE_WITH_ARGUMENT))

    def test_debug_with_arguments_throws_exception(self):
        log = Logger()
        log.debugMode()

        # no exception
        log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')


    def test_warn_with_arguments_throws_exception(self):
        log = Logger()

        # no exception
        log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')


    def test_error_with_arguments_throws_exception(self):
        log = Logger()

        # no exception
        log.debug(MESSAGE_WITH_ARGUMENT, '1', 'too many args')

if __name__ == '__main__':
    unittest.main()
