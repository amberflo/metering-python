import unittest

from metering.logger import Logger

MESSAGE = 'my message'
MESSAGE_WITH_ARGUMENT = 'error uploading: %s'
AMBERFLO_LOGGER = 'amberflo'

class TestLogger(unittest.TestCase):
    """Test class for Logger"""

    def test_debug(self):
        log = Logger()
        log.debugMode()

        with self.assertLogs(AMBERFLO_LOGGER, level='DEBUG') as cm:
            log.debug(MESSAGE)

        expectedMessage = "DEBUG:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE)
        self.assertEqual(cm.output, [expectedMessage])


    def test_warn(self):
        log = Logger()

        with self.assertLogs(AMBERFLO_LOGGER, level='WARN') as cm:
            log.warn(MESSAGE)

        expectedMessage = "WARNING:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE)
        self.assertEqual(cm.output, [expectedMessage])


    def test_error(self):
        log = Logger()

        with self.assertLogs(AMBERFLO_LOGGER, level='ERROR') as cm:
            log.error(MESSAGE)

        expectedMessage = "ERROR:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE)
        self.assertEqual(cm.output, [expectedMessage])


    def test_debug_with_arguments(self):
        log = Logger()
        log.debugMode()

        with self.assertLogs(AMBERFLO_LOGGER, level='DEBUG') as cm:
            log.debug(MESSAGE_WITH_ARGUMENT, '1')

        expectedMessage = "DEBUG:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE_WITH_ARGUMENT % '1')
        self.assertEqual(cm.output, [expectedMessage])


    def test_warn_with_arguments(self):
        log = Logger()

        with self.assertLogs(AMBERFLO_LOGGER, level='WARN') as cm:
            log.warn(MESSAGE_WITH_ARGUMENT, '1')

        expectedMessage = "WARNING:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE_WITH_ARGUMENT % '1')
        self.assertEqual(cm.output, [expectedMessage])


    def test_error_with_arguments(self):
        log = Logger()

        with self.assertLogs(AMBERFLO_LOGGER, level='ERROR') as cm:
            log.error(MESSAGE_WITH_ARGUMENT, '1')

        expectedMessage = "ERROR:{0}:{1}".format(AMBERFLO_LOGGER, MESSAGE_WITH_ARGUMENT % '1')
        self.assertEqual(cm.output, [expectedMessage])

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