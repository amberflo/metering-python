import unittest

import metering


class TestModule(unittest.TestCase):

    def failed(self):
        self.failed = True

    def setUp(self):
        self.failed = False
        metering.write_key = 'testsecret'
        metering.on_error = self.failed

    def test_no_write_key(self):
        metering.write_key = None
        self.assertRaises(Exception, metering.meter)

    def test_no_host(self):
        metering.host = None
        self.assertRaises(Exception, metering.meter)

    def test_meter(self):
        metering.meter('Python Test', meter_name='python module event', meter_value=1)
        metering.flush()

    # def test_identify(self):
    #     metering.identify('userId', {'email': 'user@email.com'})
    #     metering.flush()
    #
    # def test_group(self):
    #     metering.group('userId', 'groupId')
    #     metering.flush()
    #
    # def test_alias(self):
    #     metering.alias('previousId', 'userId')
    #     metering.flush()
    #
    # def test_page(self):
    #     metering.page('userId')
    #     metering.flush()
    #
    # def test_screen(self):
    #     metering.screen('userId')
    #     metering.flush()

    def test_flush(self):
        metering.flush()
