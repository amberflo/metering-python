import unittest

from metering.ingest import get_ingest_client
from metering.ingest import IngestApiClient, IngestS3Client


class TestGetIngestClient(unittest.TestCase):
    def test_get_api_client(self):
        client = get_ingest_client(api_key="foo")
        self.assertIsInstance(client.consumers[0].backend, IngestApiClient)

    def test_get_s3_client(self):
        client = get_ingest_client(bucket_name="foo")
        self.assertIsInstance(client.consumers[0].backend, IngestS3Client)

    def test_get_s3_client_with_keys(self):
        client = get_ingest_client(
            bucket_name="foo", access_key="access_key", secret_key="secret_key"
        )
        self.assertIsInstance(client.consumers[0].backend, IngestS3Client)
