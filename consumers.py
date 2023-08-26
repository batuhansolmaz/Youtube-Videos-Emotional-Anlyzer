
from kafka import KafkaConsumer, KafkaProducer , KafkaClient
from kafka.admin import KafkaAdminClient, NewTopic, ConfigResource, ConfigResourceType ,NewPartitions
from kafka import TopicPartition
import config
import json
import msgpack
import logging

topic = config.config["kafka"]["topic"]
group_id = config.config["kafka"]["group_id"]
server = config.config["kafka"]["bootstrap_servers"]

#resets the offset to the beginning of the consumer group
def consumer_from_offset(topic, group_id, offset):
    """Return the consumer from a certain offset."""
    print("Creating consumer")
    consumer = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        group_id=group_id,
        value_deserializer=lambda value: json.loads(value.decode('ascii')),
        consumer_timeout_ms=500,
        )
    partition_info = consumer.partitions_for_topic(topic)
    
    print(partition_info)
    partitions = [TopicPartition(topic, partition) for partition in partition_info]
    consumer.assign(partitions)
    for tp in partitions:
        consumer.seek(tp, offset)
    return consumer
    

def filter_partition(topic, partition, offset , video_id):
    """Read messages from a specific partition starting from a given offset."""
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=300 , value_deserializer=lambda value: json.loads(value.decode('ascii')))
    tp = TopicPartition(topic=topic, partition=partition)
    consumer.assign([tp])
    consumer.seek(tp, offset)
    print(f"Reading topic {topic}, partition {partition}, offset {offset}")
    for message in consumer:
        return message.value["video_id"]

    consumer.close()

def read_from_partition(topic, partition, offset):
    """Read messages from a specific partition starting from a given offset."""
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=300  ,value_deserializer=lambda value: json.loads(value.decode('ascii')))
    tp = TopicPartition(topic=topic, partition=partition)
    consumer.assign([tp])
    consumer.seek(tp, offset)
    print(f"Reading topic {topic}, partition {partition}, offset {offset}")
    
    try:
        for message in consumer:
            comment = message.value["comment"]
            video_id = message.value["video_id"]
            yield {"comment": comment, "video_id": video_id}
    finally:
        consumer.close()


def consume_1_message(topic, partition, offset):
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092' ,consumer_timeout_ms= 100 ,value_deserializer=lambda value: json.loads(value.decode('ascii')))
    tp = TopicPartition(topic=topic, partition=partition)
    consumer.assign([tp])
    consumer.seek(tp, offset)
    
    for message in consumer:
        video_id = message.value["video_id"]
        print(video_id)
        return video_id
    consumer.close()


def add_partitions(topic, new_partition_count, bootstrap_servers):
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    
    topic_partitions = {
        topic: NewPartitions(new_partition_count)
    }

    # Increase the number of partitions
    admin_client.create_partitions(topic_partitions)

def get_partition_count(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=server
    )
    partitions = consumer.partitions_for_topic(topic)
    return len(partitions)

def find_partition(video_id):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=server,
        auto_offset_reset='earliest',  # Start reading from the beginning of the partition
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode('ascii'))
    )

    partitions = consumer.partitions_for_topic(topic)
    print(partitions)
    for partition in partitions:
        id = filter_partition(topic, partition, 0, video_id)
        if(video_id is not None and id == video_id):
            return partition


                
    consumer.close()

def consume_all_video_ids():
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=server,
        auto_offset_reset='earliest',  # Start reading from the beginning of the partition
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode('ascii'))
    )

    partitions = consumer.partitions_for_topic(topic)
    print(partitions)
    lst = []
    for partition in partitions:
        video_id = consume_1_message(topic, partition, 0)
        lst.append(video_id)
    consumer.close()
    print(lst)
    return lst

def consume_comments(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=server,
        group_id=group_id,
        value_deserializer=lambda value: json.loads(value.decode('ascii')),
        auto_offset_reset='earliest',
    )

    try:
        for message in consumer:
            comment_data = message.value
            comment = comment_data["comment"]
            video_id = comment_data["video_id"]
            print(f"Consumed comment: {comment}")
            print(f"Video ID: {video_id}")
           
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


def test_consumer_from_offset():
    consumer = consumer_from_offset(topic, group_id, 0)
    for message in consumer:
        consumer.commit()
        print(message.value)
        comment = message.value["comment"]
        video_id = message.value["video_id"]
        print(f"Consumed comment: {comment}")
        print(f"Video ID: {video_id}")
        yield {"comment": comment, "video_id": video_id}
    consumer.close()


def test_consume_comments():
    consume_comments(topic)



#consume_all_video_ids()

#print(get_partition_for_key("jItIQ-UvFI4"))
#test_consume_comments()