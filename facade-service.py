from flask import Flask, request, jsonify
import uuid
import requests


facade = Flask(__name__)


@facade.route('/', methods=['POST'])
def post_message():
    msg = request.get_data().decode()
    print(f"Got message: {msg}")
    key = uuid.uuid1()
    print(f"Created UUID: {key}")

    res = requests.post(facade.config["logging-service"], data={'uuid': str(key), "msg": msg})
    if res.status_code != requests.codes.ok:
        print("Can't send data to logging service")
        return jsonify(success=False, error="Can't send data to logging service", code=res.status_code)


    return jsonify(success=True)


@facade.route('/', methods=['GET'])
def get_all_strings():
    logging_res = requests.get(facade.config["logging-service"])
    if logging_res.status_code != requests.codes.ok:
        print("Can't get data from logging service")
        return jsonify(success=False, error="Can't get data from logging-service", code=logging_res.status_code)

    print("Got data from logging service")

    messages_res = requests.get(facade.config["messages-service"])
    if messages_res.status_code != requests.codes.ok:
        print("Can't get data from messages service")
        return jsonify(success=False, error="Can't get data from messages-service", code=messages_res.status_code)

    print("Got data from messages service")

    return jsonify(success=True, data=f"{logging_res.text}{messages_res.text}")





if __name__ == '__main__':
    facade.config["logging-service"] = " http://127.0.0.1:5100/"
    facade.config["messages-service"] = " http://127.0.0.1:5200/"
    facade.run()
