import os
import boto3
import datetime

from metering.ingest import create_ingest_client, create_ingest_payload


# This sample code takes the tag customer_id_tag_name and insert meters to
# amberflo using the aws service name as the meter name and the tag value as
# the customer_id
customer_id_tag_name = "custom_tag_tenant_id"


def lambda_handler(event, context):
    aws_cost_explorer_pull()


def aws_cost_explorer_pull():
    client = create_ingest_client(api_key=os.environ["API_KEY"])

    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=10)).strftime(r"%Y-%m-%d")
    end = (now - datetime.timedelta(days=1)).strftime(r"%Y-%m-%d")

    # to use a specific profile e.g. 'dev'
    session = boto3.session.Session()
    cd = session.client("ce", "us-west-2")

    results = []

    token = None
    while True:
        if token:
            kwargs = {"NextPageToken": token}
        else:
            kwargs = {}
        data = cd.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="DAILY",
            Metrics=["UsageQuantity", "UnblendedCost"],
            GroupBy=[
                # {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "TAG", "Key": customer_id_tag_name},
            ],
            **kwargs
        )
        results += data["ResultsByTime"]
        token = data.get("NextPageToken")
        if not token:
            break
    print(results)
    print(
        "\t".join(
            ["TimePeriod", "LinkedAccount", "Service", "Amount", "Unit", "Estimated"]
        )
    )
    for result_by_time in results:
        for group in result_by_time["Groups"]:
            amount = group["Metrics"]["UsageQuantity"]["Amount"]
            # unit = group["Metrics"]["UsageQuantity"]["Unit"]
            customer_id = group["Keys"][1]
            customer_id = customer_id.replace(customer_id_tag_name + "$", "")
            # skip if not tagged
            if not customer_id:
                continue
            print(group)
            service_name = group["Keys"][0]
            # print(result_by_time['TimePeriod']['End'], '\t', '\t'.join(group['Keys']), '\t', amount, '\t', unit, '\t', result_by_time['Estimated'])
            date_time_obj = datetime.datetime.strptime(
                result_by_time["TimePeriod"]["End"], "%Y-%m-%d"
            )
            # print(date_time_obj)
            time_in_millis = int(date_time_obj.timestamp() * 1000)
            # time_in_millis = int(round(time.time() * 1000))
            # we ingest to amberflo with dedup on the date, so we can run this multiple times a day without duplicates
            event = create_ingest_payload(
                service_name.replace(" ", "_"),
                (float(amount)),
                unique_id=str(time_in_millis),
                meter_time_in_millis=time_in_millis,
                customer_id=customer_id,
                dimensions={},
            )
            client.send(event)
            cost_amount = group["Metrics"]["UnblendedCost"]["Amount"]
            event = create_ingest_payload(
                service_name.replace(" ", "_") + "_cost",
                (float(cost_amount)),
                unique_id=str(time_in_millis),
                meter_time_in_millis=time_in_millis,
                customer_id=customer_id,
                dimensions={},
            )
            client.send(event)

    client.shutdown()


if __name__ == "__main__":
    aws_cost_explorer_pull()
