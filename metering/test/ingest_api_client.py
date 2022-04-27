import os
import unittest
from time import time

from metering.ingest import (
    IngestApiClient,
    create_ingest_payload,
)

API_KEY = os.environ["TEST_API_KEY"]


class TestIngestApiClient(unittest.TestCase):
    def setUp(self):
        self.client = IngestApiClient(API_KEY)

        meter_api_name = "my meter"
        meter_float_value = 1.2
        customer_id = "123"
        timestamp = int(round(time() * 1000))

        self.meters = [
            create_ingest_payload(
                meter_api_name=meter_api_name,
                meter_value=meter_float_value,
                meter_time_in_millis=timestamp + 10 * i,
                customer_id=customer_id,
            )
            for i in range(10)
        ]

    def test_can_send_one_meter(self):
        response = self.client.send(self.meters[0])
        self.assertEqual(response, "1 records were ingested")

    def test_can_send_many_meters(self):
        response = self.client.send(self.meters)
        self.assertEqual(response, "{} records were ingested".format(len(self.meters)))
