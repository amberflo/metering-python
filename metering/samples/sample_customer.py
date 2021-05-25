import metering


def setup_customer():
    # obtain your Amberflo API Key
    metering.api_key = 'my-api-key'

    # traits are optional. Traits can be used as filters or aggregation buckets.
    customer = metering.add_or_update_customer(
        customer_id='1234',
        customer_name='Stark Industries',
        traits={'region': 'midwest', 'stripeId': 'cus_AJ6bY3VqcaLAEs'})
    print(customer)


setup_customer()
