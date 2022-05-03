from metering.ingest.api_client import IngestApiClient, create_ingest_payload  # noqa
from metering.ingest.s3_client import IngestS3Client
from metering.ingest.producer import ThreadedProducer


def get_ingest_client(
    api_key=None, bucket_name=None, access_key=None, secret_key=None, **kwargs
):
    """
    Convenience method to instantiate a threaded ingest client.
    """
    if api_key:
        return ThreadedProducer({"api_key": api_key}, **kwargs)

    params = {
        "bucket_name": bucket_name,
        "access_key": access_key,
        "secret_key": secret_key,
    }
    return ThreadedProducer(params, IngestS3Client)
