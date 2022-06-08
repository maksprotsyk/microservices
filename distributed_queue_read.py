import hazelcast
import random

client = hazelcast.HazelcastClient(
    cluster_name="distributed_map"
)
distributed_queue = client.get_queue("my-distributed-queue").blocking()

while True:
    try:
        print(f"Got: {distributed_queue.take()}")
    except KeyboardInterrupt:
        break

print("Finished")

client.shutdown()