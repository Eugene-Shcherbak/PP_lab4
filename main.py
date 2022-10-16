from flask import Flask
from waitress import serve


app = Flask(__name__)


@app.route("/api/v1/hello-world-29")
def hello():
    return "Hello World 29"


if __name__ == "__main__":
    serve(app)
