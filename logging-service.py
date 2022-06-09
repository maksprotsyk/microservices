from flask import Flask, request, jsonify
import sys
import hazelcast
import consul


logging = Flask(__name__)


@logging.route('/', methods=['POST'])
def save_message():
    print(request.form)
    msg = request.form["msg"]
    print(f"Got message: {msg}")
    key = request.form["uuid"]
    print(f"Got UUID: {key}")

    logging.config["map"].put(key, msg)

    return jsonify(success=True)


@logging.route('/', methods=['GET'])
def get_all_strings():
    return "".join(logging.config["map"].values())


def main():
    if len(sys.argv) == 1:
        return
    port = int(sys.argv[1])

    logging.config["consul"] = consul.Consul()
    cluster_name = logging.config["consul"].kv.get("cluster_name")[1]["Value"].decode()
    client = hazelcast.HazelcastClient(
        cluster_name=cluster_name
    )

    map_name = logging.config["consul"].kv.get("map_name")[1]["Value"].decode()
    logging.config["map"] = client.get_map(
        map_name
    ).blocking()

    name = f"logging:{port}"
    logging.config["consul"].agent.service.register(
        name=name,
        service_id=name,
        tags=["logging"],
        address="http://127.0.0.1", port=port,
    )

    logging.run(port=port)


if __name__ == '__main__':
    main()
