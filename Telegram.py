import dataclasses
import io
from typing import final
from config import config
from telegram import InputFile, Update
from telegram.ext import CommandHandler, MessageHandler, filters , ContextTypes ,Application
import re
import EmotionAnalyzer
import consumers
import Youtube
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

Token: final = config["telegram_token"]
BotName: final = "yt_comment_bot"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello! I'm {BotName}. I can help you to analyze Youtube comments. Send me a Youtube video URL and I'll tell you what I think about it.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a Youtube video URL or Youtube playlist URL and I'll tell you what I think about it.")

def handle_response(text : str):
    if text == "hi":
        return "Hello"
    
def extract_id_from_url(url):
    # Define the regular expression patterns for video and playlist URLs
    video_pattern = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
    playlist_pattern = r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
    
    # Search for the patterns in the URL
    video_match = re.search(video_pattern, url)
    playlist_match = re.search(playlist_pattern, url)
    
    if video_match:
        return video_match.group(1), "video"
    elif playlist_match:
        return playlist_match.group(1), "playlist"
    else:
        return None, "unknown"

def plot_emotions(emotions , video_id):
    labels = list(emotions.keys())
# Values for the pie chart
    values = list(emotions.values())

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f'Emotion Analysis for: {generate_youtube_url(video_id)}')
    # Save the chart as an image in memory
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()
    return img_buffer

async def send_pie_chart(update: Update, context: ContextTypes.DEFAULT_TYPE , img_buffer):
    # Send the pie chart image to the chat
    img_buffer.seek(0)
    img_bytes = img_buffer.read()
    # Send the pie chart image to the chat
    print(update.message.chat_id)
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=InputFile(io.BytesIO(img_bytes), filename='pie_chart.png'))

def generate_youtube_url(video_id):
    return f"https://www.youtube.com/watch?v={video_id}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = str(update.message.text)
    id = update.message.chat.id
    id, type = extract_id_from_url(text)
    if(type == "video"):
        if(EmotionAnalyzer.check_if_video_exists(id)):
            response = "Thank you for your video. I have analyzed it and here is what I think about it:\n"

            data = EmotionAnalyzer.fetch_video_data(id)
            print(data)
            await send_pie_chart(update, context, plot_emotions(data ,id))
        else:
            Youtube.create_topic_if_not_exists(config["kafka"]["bootstrap_servers"], config["kafka"]["topic"], 0, 1)
            partition_count=consumers.get_partition_count(config["kafka"]["topic"])
            #add 1 partition
            consumers.add_partitions(config["kafka"]["topic"], partition_count+1, config["kafka"]["bootstrap_servers"])
            Youtube.produce_comments(id , partition_count)
            EmotionAnalyzer.consume_last_and_send_to_elastic(id , partition_count)
            response = "Thank you for your video. I have analyzed it and here is what I think about it:\n"
            await update.message.reply_text(response) 
            data = EmotionAnalyzer.fetch_video_data(id)
            await send_pie_chart(update, context, plot_emotions(data ,id))
        await update.message.reply_text(response) 
        
    elif(type == "playlist"):
        video_ids = Youtube.fetchAllVideoIds(id)
        response = "Thank you for your playlist. I have analyzed it and here is what I think about it:\n"
        await update.message.reply_text(response)
        Youtube.create_topic_if_not_exists(config["kafka"]["bootstrap_servers"], config["kafka"]["topic"], 0, 1)
        for video_id in video_ids:
            if(EmotionAnalyzer.check_if_video_exists(video_id)):
                await send_pie_chart(update, context, plot_emotions(EmotionAnalyzer.fetch_video_data(video_id) ,video_id))
            else:
                partition_count=consumers.get_partition_count(config["kafka"]["topic"])
                #add 1 partition
                consumers.add_partitions(config["kafka"]["topic"], partition_count+1, config["kafka"]["bootstrap_servers"])
                Youtube.produce_comments(video_id, partition_count)
                EmotionAnalyzer.consume_last_and_send_to_elastic(video_id, partition_count)
                await send_pie_chart(update, context, plot_emotions(EmotionAnalyzer.fetch_video_data(video_id) ,video_id))
    else:
        await update.message.reply_text("Please send me a Youtube video URL or Youtube playlist URL and I'll tell you what I think about it.")


async def send_changes_on_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE , message):
    await context.bot.send_message(chat_id=update.message.chat_id, text=message)

async def unsubscribe_command(update, context):
    args = context.args
    if len(args) == 1:
        id_to_unsubscribe = extract_id_from_url(args[0])
        EmotionAnalyzer.delete_video_data(id_to_unsubscribe)
        response = f"Unsubscribed from {id_to_unsubscribe}"
    else:
        response = "Invalid usage. Please provide a video_url."

    await update.message.reply_text(response)

async def list_command(update, context):
    video_ids = EmotionAnalyzer.fetch_all_video_ids_from_elasticsearch("youtube")
    response = "Subscribed to the following videos:\n"
    for video_id in video_ids:
        response += f"{generate_youtube_url(video_id)}\n"
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print("Starting bot")
    app = Application.builder().token(Token).build()

    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CommandHandler("list", list_command))
    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, send_changes_on_emotions))
    #errors
    app.add_error_handler(error)

    print("Bot started")
    app.run_polling(poll_interval=0.5)