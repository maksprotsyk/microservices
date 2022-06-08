import hazelcast

client = hazelcast.HazelcastClient(
    cluster_members="distributed_map"
)
print("Connected")

distributed_map = client.get_map("my-distributed-map").blocking()
print("Created the map")

for i in range(0, 1000):
    distributed_map.put(i, 0)
print("Finished")

client.shutdown()
