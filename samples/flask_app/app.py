import logging
from flask import Flask

from amberflo.decorator import count_api_calls
from amberflo.middleware import init_amberflo

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
init_amberflo(app)


@app.route("/api/foo/")
@count_api_calls
def get_foo():
    return {"foo": "bar"}


@app.route("/api/bar/")
@count_api_calls
def get_bar():
    return {"bar": "foo"}


@app.route("/")
def hello_world():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True)
