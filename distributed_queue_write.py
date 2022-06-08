import hazelcast
import random

client = hazelcast.HazelcastClient(
    cluster_name="distributed_map"
)
distributed_queue = client.get_queue("my-distributed-queue").blocking()

while True:
    try:
        val = random.randint(1, 10)
        distributed_queue.put(random.randint(1, 10))
        print(f"Added: {val}")
    except KeyboardInterrupt:
        break

print("Finished")

client.shutdown()
