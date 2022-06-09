from flask import Flask, request, jsonify
import uuid
import requests
import random
import hazelcast


facade = Flask(__name__)


@facade.route('/', methods=['POST'])
def post_message():
    msg = request.get_data().decode()
    print(f"Got message: {msg}")
    key = uuid.uuid1()
    print(f"Created UUID: {key}")

    facade.config["queue"].put(msg)

    indexes = list(range(len(facade.config["logging-service"])))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            res = requests.post(
                facade.config["logging-service"][ind],
                data={'uuid': str(key), "msg": msg}
            )
            break
        except requests.exceptions.ConnectionError:
            continue
    else:
        return jsonify(success=False, error="Logging service is not available", code=-2)

    if res.status_code != requests.codes.ok:
        print("Can't send data to logging service")
        return jsonify(success=False, error="Can't send data to logging service", code=res.status_code)

    return jsonify(success=True)


@facade.route('/', methods=['GET'])
def get_all_strings():
    indexes = list(range(len(facade.config["logging-service"])))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            logging_res = requests.get(
                facade.config["logging-service"][ind]
            )
            break
        except requests.exceptions.ConnectionError:
            continue
    else:
        return jsonify(success=False, error="Logging service is not available", code=-2)

    if logging_res.status_code != requests.codes.ok:
        print("Can't get data from logging service")
        return jsonify(success=False, error="Can't get data from logging-service", code=logging_res.status_code)

    print("Got data from logging service")

    indexes = list(range(len(facade.config["messages-service"])))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            messages_res = requests.get(
                facade.config["messages-service"][ind]
            )
            break
        except requests.exceptions.ConnectionError:
            continue
    else:
        return jsonify(success=False, error="Messages service is not available", code=-2)

    if messages_res.status_code != requests.codes.ok:
        print("Can't get data from messages service")
        return jsonify(success=False, error="Can't get data from messages-service", code=messages_res.status_code)

    print("Got data from messages service")

    return jsonify(success=True, data=f"{logging_res.text}{messages_res.text}")


def main():
    client = hazelcast.HazelcastClient(
        cluster_name="distributed_map"
    )
    facade.config["logging-service"] = ["http://127.0.0.1:5100/", "http://127.0.0.1:5101/", "http://127.0.0.1:5102/"]
    facade.config["messages-service"] = ["http://127.0.0.1:5201/", "http://127.0.0.1:5202/"]
    facade.config["queue"] = client.get_queue("messages-queue").blocking()
    facade.run()


if __name__ == '__main__':
    main()
