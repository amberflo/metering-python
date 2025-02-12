# Release History

## 3.3.0
Features:
- New `meter_llm` decorator to allow automatic extraction and ingestion of llm responses into Amberflo
- Sample script to automaticaly create templated "input_tokens" and "output_tokens" meters as well as a "test_customer" to get started with the decorator

## 3.2.0
Features:
- Allow ingestion of arbitrary payload through schema detection

## 3.0.1

Features:
- Use highly available ingest API endpoint
- Allow customizing backoff delay on ingest consumer

## 3.0.0

**Breaking Changes:**
- Module layout has changed, as well as some class names and methods
- The package level interfaces (e.g. `metering.add_or_update_customer`) have been deprecated; some global methods like `metering.meter` are still available, but not all of them; their use is discouraged.

Features:
- More APIs were added
    - Customer Product Plan
    - Customer Portal Session
    - Customer Prepaid Order
    - Customer Product Invoice
- Existing APIs were improved
    - Customer (list, get, add, update, create_in_stripe option)
    - Usage (get multiple requests at once)
- It is now possible to control logging at the module level

Miscelaneous:
- Improved payload validation on factory functions
- Test suite was improved
- Collected and updated all samples into this repository

## 2.3.0

Fixes:
- Remove constraint that uniqueId should be UUID.

## 2.2.0

Fixes:
- When uploading to S3, credentials do not work.
- Logging is not working when set to DEBUG
- uniqueId is not random if done within short interval of time
- S3 Filename logic is wrong, has special characters

## 2.1.0

Features:
- Add S3 ingestion client

## 2.0.0

- Added UsageClient
- Added CustomerApiClient
- Refactored MeterFactory to change message property names to camel case, updated names, and remove customer name.
- Added metering/samples for usage and customer

## 1.0.7

- Changed the `customer_id` and `customer_info` to be mandatory fields.

## 1.0.6

- Dropped support of Python versions before 3.5.
- Changed the `utc_time_millis` to be a mandatory field.

## 1.0.5

- Changed user/password authentication to an app_key.
- Small changes to the meter api:
  - Change `tenant` to `customer_name` arg.
  - Added a `customer_id` arg.
  - Added a `unique_id` arg.
  - `dimensions` is now a simple string to string map.
- Improved the meter api args validations logic.
- Removed the gzip app from the client api.
- Safer logging, and more robust client (handle exceptions better).
- Moved a few "responsibilities" to their own classes (logging, validation, meter message creation).
- Documented code and added unit tests.

## 1.0.0

- Initial release
