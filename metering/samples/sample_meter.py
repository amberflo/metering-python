import metering
import time


def send_meter():
    metering.app_key = "8eff6750-e325-11eb-a3b6-ff820190b139"
    # metering.debug = True
    current_time = int(round(time.time() * 1000))
    dimensions = {"region": "us-east-1"}

    metering.meter(
        meter_api_name="cluster_count",
        meter_value=5,
        meter_time_in_millis=current_time,
        customer_id="54a43bba-915d-4512-a0bd-9d9debe2eb3a",
        dimensions=dimensions,
    )

    metering.flush()
    metering.shutdown()


def send_meter_to_s3(with_credentials=False):
    # use your aws access key and secret key along with s3 bucket
    if with_credentials:
        metering.access_key = "aws_access_key"
        metering.secret_key = "aws_secret_key"

    metering.s3_bucket = "s3-bucket-name"
    metering.debug = True
    current_time = int(round(time.time() * 1000))
    dimensions = {"region": "us-east-1"}

    metering.meter(
        meter_api_name="cluster_count",
        meter_value=5,
        meter_time_in_millis=current_time,
        customer_id="54a43bba-915d-4512-a0bd-9d9debe2eb3a",
        dimensions=dimensions,
    )

    metering.flush()
    metering.shutdown()


# send_meter()
send_meter_to_s3()
