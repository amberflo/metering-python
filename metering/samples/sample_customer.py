import metering


def setup_customer():
    # obtain your Amberflo API Key
    metering.app_key = 'app_key'

    # traits are optional. Traits can be used as filters or aggregation buckets.
    customer = metering.add_or_update_customer(
        customer_id='alpha-beta-omega-1',
        customer_name='Wayne Industries',
        traits={'region': 'us-east-1', 'stripeId': 'cus_AJ6bY3VqcaLAEs'})
    print(customer)


setup_customer()
