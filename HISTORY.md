Release History
===============

1.0.0
============
* Initial release


1.0.5
============
- Changed user/password authentication to an app_key.
- Small changes to the meter api -
    :   -   Change 'tenant' to 'customer_name' arg.
        -   Added a 'customer_id' arg.
        -   Added a 'unique_id' arg.
        -   'dimensions' is now a simple string to string map.
- Improved the meter api args validations logic.
- Removed the gzip app from the client api.
- Safer logging, and more robust client (handle exceptions better).
- Moved a few "responsibilities" to their own classes (logging, validation, meter message creation).
- Documented code and added unit tests.

1.0.6
============
- Dropped support of python versions < 3.5.
- Changed the 'utc_time_millis' to be a mandatory field.


1.0.7
============
- Changed the 'customer_id' and 'customer_info' to be mandatory fields.

2.0.0
============
- Added UsageClient
- Added CustomerApiClient
- Refactored MeterFactory to change message property names to camel case, updated names, and remove customer name. 
- Added metering/samples for usage and customer

2.1.0
============
- Add s3 ingestion client 

2.2.0
============
Fixes:
- When uploading to s3, credentials do not work.
- Logging is not working when set to DEBUG
- uniqueId is not random if done within short interval of time
- s3 Filename logic is wrong, has special characters

2.3.0
============
1. Remove constraint that uniqueId should be UUID. 