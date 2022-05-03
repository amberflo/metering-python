# Sample Code

In this folder you can find many examples of how to use this SDK.

Each sample starts with a docstring explaining it.

## How to run

Setup a virtual environment and install this SDK and some dependencies.
```
python3 -m virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

Then, pick a sample and execute it directly, e.g.:
```
./add_or_update_customer.py
```

Note that the samples connecting to external services can't be run as is.  For
instance, for the `./postgres_to_amberflo.py` example, you'll need a PostgreSQL
instance with a compatible schema.
