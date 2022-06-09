import consul

c = consul.Consul()
c.kv.put("cluster_name", "distributed_map")
c.kv.put("queue_name", "messages-queue")
c.kv.put("map_name", "messages-map")
