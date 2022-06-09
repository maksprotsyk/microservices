from flask import Flask
import hazelcast
import sys
import threading
import consul

messages = Flask(__name__)


@messages.route('/', methods=['GET'])
def get_static_string():
    messages.config["lock"].acquire()
    text = "".join(messages.config["messages"])
    messages.config["lock"].release()
    return text


def queue_reader():
    while True:
        item = messages.config["queue"].take()
        messages.config["lock"].acquire()
        messages.config["messages"].append(item)
        print(f"Got message: {item}")
        messages.config["lock"].release()


def main():
    if len(sys.argv) == 1:
        return

    port = int(sys.argv[1])
    messages.config["consul"] = consul.Consul()

    cluster_name = messages.config["consul"].kv.get("cluster_name")[1]["Value"].decode()
    client = hazelcast.HazelcastClient(
        cluster_name=cluster_name
    )

    queue_name = messages.config["consul"].kv.get("queue_name")[1]["Value"].decode()
    messages.config["queue"] = client.get_queue(
        queue_name
    ).blocking()

    messages.config["messages"] = []
    messages.config["lock"] = threading.Lock()

    thread = threading.Thread(target=queue_reader)
    thread.start()

    name = f"messages:{port}"
    messages.config["consul"].agent.service.register(
        name=name,
        service_id=name,
        tags=["messages"],
        address="http://127.0.0.1", port=port,
    )

    messages.run(port=port)

    thread.join()


if __name__ == '__main__':
    main()
