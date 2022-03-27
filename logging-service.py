from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import requests


logging = Flask(__name__)

data = {}


@logging.route('/', methods=['POST'])
def save_message():
    print(request.form)
    msg = request.form["msg"]
    print(f"Got message: {msg}")
    key = request.form["uuid"]
    print(f"Got UUID: {key}")

    data[key] = msg

    return jsonify(success=True)



@logging.route('/', methods=['GET'])
def get_all_strings():
    return "".join(data.values())





if __name__ == '__main__':
    logging.run(port=5100)
