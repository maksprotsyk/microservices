from flask import Flask, request, jsonify
import sys
import hazelcast


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


if __name__ == '__main__':
    client = hazelcast.HazelcastClient(
        cluster_name="distributed_map"
    )
    logging.config["map"] = client.get_map("messages-map").blocking()
    if len(sys.argv) != 1:
        logging.run(port=int(sys.argv[1]))
