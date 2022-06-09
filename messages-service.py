from flask import Flask
import hazelcast
import sys
import threading

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
    client = hazelcast.HazelcastClient(
        cluster_name="distributed_map"
    )
    messages.config["queue"] = client.get_queue("messages-queue").blocking()
    messages.config["messages"] = []
    messages.config["lock"] = threading.Lock()

    thread = threading.Thread(target=queue_reader)
    thread.start()

    if len(sys.argv) != 1:
        messages.run(port=int(sys.argv[1]))

    thread.join()


if __name__ == '__main__':
    main()
