
import subprocess

import schedule
import asyncio
import string
import subprocess

from kafka import KafkaProducer , KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic, ConfigResource, ConfigResourceType ,NewPartitions
from config import config
import schedule
import time
import EmotionAnalyzer
import logging
import Youtube

google_api_key = config["google_api_key"]
client_id  =config["kafka"]["client_id"]
group_id = config["kafka"]["group_id"]
server = config["kafka"]["bootstrap_servers"]
topic = config["kafka"]["topic"]

async def refresh_topic():
    video_ids=  EmotionAnalyzer.fetch_all_video_ids_from_elasticsearch("youtube")
    old_video_datas =  EmotionAnalyzer.fetch_all_video_data("youtube")
    length = len(video_ids)
    admin_client = KafkaAdminClient(bootstrap_servers=server, client_id=client_id)
    topic_list = []
    try:
        bash_command = config["kafka_topic.sh_path"]+" --bootstrap-server localhost:9092 --delete --topic youtube-comments-raw"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        print(error)
        time.sleep(5)
        print("Topic deleted: ", topic)

    except Exception as e:
        print("Error while deleting topic:", e)
        pass

    logging.info("Creating topic: ", topic)
    new_topic = NewTopic(name=topic, num_partitions=length , replication_factor=1)
    topic_list.append(new_topic)
    admin_client.create_topics(new_topics=topic_list)
    logging.info("Topic created: ", topic)
    count = 0
    for video_id in video_ids:
        print(video_id)
        Youtube.produce_comments(video_id, count)
        EmotionAnalyzer.consume_last_and_send_to_elastic(video_id ,count)
        count += 1
    
    new_video_datas= EmotionAnalyzer.fetch_all_video_data("youtube")
    await EmotionAnalyzer.detect_changes_on_emotions_and_send(old_video_datas, new_video_datas)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(refresh_topic())
    loop.close()

schedule.every().day.at("02:00").do(main)
main()
while True:
    schedule.run_pending()
    time.sleep(1)
