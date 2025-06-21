To create a topic:
```
kafka-topics --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

To list the topics:
```
kafka-topics --list --bootstrap-server localhost:9092
```

To change number of partitions in a topic:
```
kafka-topics --bootstrap-server localhost:9092 --alter --topic test-topic --partitions 3
```

To delete a topic:
```
kafka-topics --bootstrap-server localhost:9092 --delete --topic test-topic
```

Run the consumer and publisher with:
```
python3 consumer.py
python3 publisher.py
```