import asyncio
import string
import subprocess
import sys
import json
import requests
import json
from kafka import KafkaProducer 
from kafka.admin import KafkaAdminClient, NewTopic
from config import config
import schedule
import time
import EmotionAnalyzer
import logging
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from kafka import KafkaConsumer, TopicPartition
google_api_key = config["google_api_key"]
client_id  =config["kafka"]["client_id"]
group_id = config["kafka"]["group_id"]

server = config["kafka"]["bootstrap_servers"]

topic = config["kafka"]["topic"]

producer = KafkaProducer(
    bootstrap_servers=server,
    client_id=client_id,
)

kafka_config = config["kafka"] | {"bootstrap.servers": config["kafka"]["bootstrap_servers"]
    , "client.id": client_id
    , "topic": topic
    , "group.id": group_id
}

def fetchVideos(playlistId , nextPageToken=None):
    
    playlistId = config["playlistId"]
    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={"key": google_api_key , "playlistId" : playlistId, "part": "contentDetails" , "pageToken": nextPageToken, "maxResults": 20 })

    data = json.loads(response.text)
    print(data)
    return data

def fetchAllVideoIds(playlistId):
    video_ids = []  
    nextPageToken = None
    while True:
        data = fetchVideos(playlistId ,nextPageToken)
        items = data.get("items", [])
        for video in items:
            video_id = video["contentDetails"]["videoId"]
            video_ids.append(video_id)  
        
        nextPageToken = data.get("nextPageToken")
        if not nextPageToken:
            break
    
    return video_ids


def fetchCommentDatas(video_id, nextPageToken=None):
    response = requests.get("https://www.googleapis.com/youtube/v3/commentThreads", params={"key": google_api_key , "videoId" : video_id, "part": "snippet" , "pageToken": nextPageToken, "maxResults": 50 })
    data = json.loads(response.text)
    return data

def fetchAllCommentDatas(video_id):
    comments = []
    nextPageToken = None
    while True:
        data = fetchCommentDatas(video_id, nextPageToken)
        items = data.get("items", [])
        for comment in items:
            comment = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        nextPageToken = data.get("nextPageToken")
        if not nextPageToken:
            break
    return comments


def produce_comments(video_id , partition):
    comments = fetchAllCommentDatas(video_id)
    producer = KafkaProducer(
    bootstrap_servers=server,
    client_id=client_id,
    value_serializer=lambda v: json.dumps(v).encode('ascii'),
    )

    for comment in comments:
        partition_key = video_id.encode('ascii')  # Use video_id as the partition key
        print(partition_key)
        lowerComment = comment.lower()
        comment = lowerComment.translate(str.maketrans('', '', string.punctuation))
        data = {"video_id": video_id, "comment": comment}
        producer.send(topic,key=partition_key, value= data , partition=partition)
        print(f"Produced comment: {comment}")

    producer.flush()
    producer.close() 

def create_topic_if_not_exists(bootstrap_servers, topic_name, partitions, replication_factor):
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    
    existing_topics = admin_client.list_topics()
    if topic_name in existing_topics:
        print(f"Topic '{topic_name}' already exists.")
    else:
        new_topic = NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)
        try:
            admin_client.create_topics(new_topics=[new_topic])
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")



