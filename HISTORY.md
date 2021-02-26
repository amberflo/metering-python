Release History
===============

1.0.0
============
* Initial release


1.0.5
============
- Changed user/password authentication to an app_key.
- Small changes to the meter api -
    :   -   Change 'tenant' to 'customer_name' arg
        -   Added a 'customer_id' arg
        -   Added a 'unique_id' arg
        -   'dimensions' is now a simple string to string map.
- Improved the meter api args validations logic.
- Removed the gzip app from the client api.
- Safer logging, and more robust client (handle exceptions better).
- Moved a few "responsibilities" to thier own classes (logging, validation, meter message creation).
- Documented code and added unit tests.
