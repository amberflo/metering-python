# Flask App Sample

This is a minimal Flask app showing how to integrate with [Amberflo](https://amberflo.io).

## Highlights

The interesting code is in the `amberflo` module.

It contains a `decorator` for counting API calls by customer, and a
`middleware` for recording the processing time of the API calls.

## How to run

Setup a virtual environment and install the SDK.
```
python3 -m virtualenv venv
. venv/bin/activate
pip install -r ./requirements.txt
```

Then, run the Django app locally:
```
export AMBERFLO_API_KEY=<api-key>
python3 app.py
```

Finally, make some API calls and check the logs:
```
curl http://127.0.0.1:5000/api/bar/
curl http://127.0.0.1:5000/api/foo/
```
