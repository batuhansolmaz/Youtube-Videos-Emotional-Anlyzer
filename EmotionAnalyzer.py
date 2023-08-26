import asyncio
import time
from transformers import pipeline

import consumers
from config import config
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging
import threading
import telegram
es = Elasticsearch("http://localhost:9200")  

topic = config["kafka"]["topic"]
group_id = config["kafka"]["group_id"]
client_id = config["kafka"]["client_id"]

classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=7)

def get_emotions(comment):
    data  = classifier(comment, max_length=512, truncation=True)
    datas = data[0] 
    return datas

def consume_last_and_send_to_elastic(video_id , partition):
    video_exist = check_if_video_exists(video_id)
    print(video_exist)
    fetchAllCommentDatas = consumers.read_from_partition(topic, partition, 0)
    get_average_emotions(list(fetchAllCommentDatas), video_exist)

def get_average_emotions(fetchAllCommentDatas , video_exist=False , consume_multiple= False):
    result_dict= {"anger":0 , "joy":0, "sadness":0, "surprise":0, "fear":0 , "disgust":0 , "neutral":0}
    my_set = set()
    prev_video_id = None
    counter = 0
    real_counter = 0
    if (not video_exist or consume_multiple) :
        for comment in fetchAllCommentDatas:
            real_counter+=1
            counter += 1
            if comment is None:
                break
            #crete hash set for video id
            video_id = comment["video_id"]
            if video_id in my_set:
                print("video is in set")
                prev_video_id = video_id
            else:
                my_set.add(video_id)
                print(my_set)
                if(prev_video_id is None):
                    continue
                for key in result_dict:
                    result_dict[key] /= counter-1
                logging.info(result_dict)
                send_to_elastic(result_dict, prev_video_id) 
                result_dict = {"anger":0 , "joy":0, "sadness":0, "surprise":0, "fear":0 , "disgust":0 , "neutral":0}
                counter = 1
            
            comment_text = comment["comment"]
            comment_emotions = get_emotions(comment_text)
            
            for i in comment_emotions:
                result_dict[i.get("label")] += i.get("score")

            if(real_counter == len(fetchAllCommentDatas)):
                    for key in result_dict:
                        result_dict[key] /= counter-1
                    logging.info(result_dict)
                    send_to_elastic(result_dict, prev_video_id) 
                    result_dict = {"anger":0 , "joy":0, "sadness":0, "surprise":0, "fear":0 , "disgust":0 , "neutral":0}
                    counter = 0
    else:
        for comment in fetchAllCommentDatas:
            video_id = comment["video_id"]
            comment_text = comment["comment"]
            comment_emotions = get_emotions(comment_text)
            
            for i in comment_emotions:
                result_dict[i.get("label")] += i.get("score")
        for key in result_dict:
            result_dict[key] /= len(fetchAllCommentDatas)

        update_elastic_doc(video_id , result_dict)
        logging.info("UPDATED WİTH SUCCESS")

        

async def detect_changes_on_emotions_and_send(old_emotions, new_emotions):
    bot = telegram.Bot(token=config["telegram_token"])
    for key in new_emotions:
        print(key)
        if(new_emotions.get(key) != old_emotions.get(key)):
            print("changes")
            response = f"Changes for {key}:\n"

            for emotion in new_emotions.get(key):
                print(emotion)
                dif = new_emotions.get(key).get(emotion) - old_emotions.get(key).get(emotion)
                print(dif)
                if(dif > 0):
                    response += f"{dif * 100} percent increase for {emotion}\n"
                elif(dif < 0):
                    response +=f"{-dif * 100} percent decrease for {emotion}\n"
                elif(dif == 0):
                    response += "no change for " + emotion + "\n"
            await bot.send_message(chat_id=config["telegram_chat_id"], text=response)

        response = f"No changes for {key}"
        await bot.send_message(chat_id=config["telegram_chat_id"], text=response) 

def send_to_elastic(data_list, video_id):
    actions = []
    #visualize all data in kibana
    action = {
        "_index": "youtube",
        "_source": {"emotions" : data_list},
        "_id": video_id
    }
    actions.append(action)

    helpers.bulk(es, actions=actions)

def delete_index():
    es.indices.delete(index="youtube", ignore=[400, 404])
    logging.info("index deleted")

def create_index():
    es.indices.create(index="youtube", ignore=400)
    logging.info("index created")

def fetch_all_video_ids_from_elasticsearch(index):
    query = {
        "query": {
            "match_all": {}  # Match all documents
        },
        "_source": ["_id"]  # Include only the _id field
    }

    result = es.search(index=index, body=query, size=10000)  # Adjust size as needed
    video_ids = [hit["_id"] for hit in result["hits"]["hits"]]
    return video_ids

def fetch_video_data(video_id):
    # Specify the index and ID you want to fetch
    index = "youtube"
    doc_id = video_id
    emotions_to_fetch = ["anger", "joy", "sadness", "surprise", "fear", "disgust", "neutral"]

    # Fetch the document
    doc = es.get(index=index, id=doc_id)

    # Extract emotion scores from the document
    emotions_scores = doc["_source"]["emotions"]

    # Filter and display scores for the specified emotions
    emotion_scores= {"anger":0 , "joy":0, "sadness":0, "surprise":0, "fear":0 , "disgust":0 , "neutral":0}
    for emotion in emotions_to_fetch:
        score = emotions_scores.get(emotion, 0.0)  # Default to 0.0 if emotion not found
        score_percent = score * 100
        emotion_scores[emotion] = score_percent
        
    return emotion_scores

def fetch_all_video_data(index_name):
    # Fetch all documents from the Elasticsearch index
    search_query = {
        "query": {
            "match_all": {}
        }
    }
    response = es.search(index=index_name, body=search_query, size=10000)  # Adjust size as needed
    
    video_data_dict = {}
    for hit in response["hits"]["hits"]:
        video_id = hit["_id"]
        emotion_scores = hit["_source"]["emotions"]
        video_data_dict[video_id] = emotion_scores
    
    return video_data_dict

def delete_video_data(index, video_id): 
    try:
        response = es.delete(index=index, id=video_id)
        if response.get("result") == "deleted":
            print(f"Video data with ID {video_id} deleted successfully.")
        else:
            print(f"Failed to delete video data with ID {video_id}.")
    except Exception as e:
        print(f"An error occurred while deleting video data: {str(e)}")

def update_elastic_doc(video_id , new_emotions_scores):
    # Create the update script
    update_script = {
        "script": {
            "source": "ctx._source.emotions = params.emotions",
            "lang": "painless",
            "params": {
                "emotions": new_emotions_scores
            }
        }
    }
    # Perform the update
    es.update(index= "youtube", id=video_id, body=update_script)


def check_if_video_exists(video_id):
    index = "youtube"

    query = {
        "query": {
            "term": {
                "_id": video_id
            }
        }
    }

    # Execute the query
    result = es.search(index=index, body=query)

    # Check if any hits were found
    if result['hits']['total']['value'] > 0:
        print("Document exists")
        return True  # Document with video_id exists
    else:
        return False  # Document with video_id does not exist



