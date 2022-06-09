from flask import Flask, request, jsonify
import uuid
import requests
import random
import hazelcast
import consul


facade = Flask(__name__)


@facade.route('/', methods=['POST'])
def post_message():
    msg = request.get_data().decode()
    print(f"Got message: {msg}")
    key = uuid.uuid1()
    print(f"Created UUID: {key}")

    facade.config["queue"].put(msg)

    services = facade.config["consul"].agent.services()

    logging_services = []

    for name, service in services.items():
        if "logging" not in service["Tags"]:
            continue
        logging_services.append(service)

    indexes = list(range(len(logging_services)))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            address = f"{logging_services[ind]['Address']}:{logging_services[ind]['Port']}/"
            res = requests.post(
                address,
                data={'uuid': str(key), "msg": msg}
            )
            break
        except requests.exceptions.ConnectionError:
            facade.config["consul"].agent.deregister(logging_services[ind]["ID"])
            continue
    else:
        return jsonify(success=False, error="Logging service is not available", code=-2)

    if res.status_code != requests.codes.ok:
        print("Can't send data to logging service")
        return jsonify(success=False, error="Can't send data to logging service", code=res.status_code)

    return jsonify(success=True)


@facade.route('/', methods=['GET'])
def get_all_strings():

    services = facade.config["consul"].agent.services()

    logging_services = []
    messages_services = []

    for name, service in services.items():
        if "logging" in service["Tags"]:
            logging_services.append(service)
        elif "messages" in service["Tags"]:
            messages_services.append(service)

    indexes = list(range(len(logging_services)))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            address = f"{logging_services[ind]['Address']}:{logging_services[ind]['Port']}/"
            logging_res = requests.get(
                address
            )
            break
        except requests.exceptions.ConnectionError:
            facade.config["consul"].agent.deregister(logging_services[ind]["ID"])
            continue
    else:
        return jsonify(success=False, error="Logging service is not available", code=-2)

    if logging_res.status_code != requests.codes.ok:
        print("Can't get data from logging service")
        return jsonify(success=False, error="Can't get data from logging-service", code=logging_res.status_code)

    print("Got data from logging service")

    indexes = list(range(len(messages_services)))
    random.shuffle(indexes)

    for ind in indexes:
        try:
            address = f"{messages_services[ind]['Address']}:{messages_services[ind]['Port']}/"
            messages_res = requests.get(
                address
            )
            break
        except requests.exceptions.ConnectionError:
            facade.config["consul"].agent.deregister(messages_services[ind]["ID"])
            continue
    else:
        return jsonify(success=False, error="Messages service is not available", code=-2)

    if messages_res.status_code != requests.codes.ok:
        print("Can't get data from messages service")
        return jsonify(success=False, error="Can't get data from messages-service", code=messages_res.status_code)

    print("Got data from messages service")

    return jsonify(success=True, data=f"{logging_res.text}{messages_res.text}")


def main():
    facade.config["consul"] = consul.Consul()

    cluster_name = facade.config["consul"].kv.get("cluster_name")[1]["Value"].decode()
    client = hazelcast.HazelcastClient(
        cluster_name=cluster_name
    )

    queue_name = facade.config["consul"].kv.get("queue_name")[1]["Value"].decode()
    facade.config["queue"] = client.get_queue(
        queue_name
    ).blocking()
    facade.run()


if __name__ == '__main__':
    main()
