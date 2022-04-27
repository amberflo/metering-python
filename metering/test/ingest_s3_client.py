import os
import unittest
from time import time

from metering.ingest import create_meter_payload
from metering.ingest import IngestS3Client

BUCKET_NAME = os.environ.get("TEST_BUCKET_NAME")
ACCESS_KEY = os.environ.get("TEST_ACCESS_KEY")
SECRET_KEY = os.environ.get("TEST_SECRET_KEY")


class TestIngestS3Client(unittest.TestCase):
    """
    When running these tests, Python will show warnings:
    > ResourceWarning: unclosed

    This is not ideal, but also not a problem.
    See:
        https://github.com/boto/boto3/issues/454#issuecomment-1047277122
    """

    def setUp(self):
        self.client = IngestS3Client(BUCKET_NAME, ACCESS_KEY, SECRET_KEY)

        meter_api_name = "my meter"
        meter_float_value = 1.2
        customer_id = "123"
        timestamp = int(round(time() * 1000))

        self.meters = [
            create_meter_payload(
                meter_api_name=meter_api_name,
                meter_value=meter_float_value,
                meter_time_in_millis=timestamp + 10 * i,
                customer_id=customer_id,
            )
            for i in range(10)
        ]

    @unittest.skipIf(BUCKET_NAME is None, "Needs S3 credentials")
    def test_can_send_one_meter(self):
        response = self.client.send(self.meters[0])
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

    @unittest.skipIf(BUCKET_NAME is None, "Needs S3 credentials")
    def test_can_send_many_meters(self):
        response = self.client.send(self.meters)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
