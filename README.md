# YouTube-Videos-Emotional-Analyzer

## Project Overview
The **YouTube Videos Emotional Analyzer** is an innovative solution designed to provide users with deep insights into the emotional landscape of YouTube video comments. In today's digital age, where video content has become an essential medium for communication, understanding the emotional responses of viewers is crucial for content creators, marketers, and researchers. This project addresses this need by offering a streamlined process for analyzing and visualizing emotional trends within YouTube video comment sections.

### Key Features

1. **Automated Emotional Analysis:** The project automates the process of collecting comments from YouTube videos, extracting emotional tones, and generating analytical reports. By leveraging Natural Language Processing (NLP) techniques, the system categorizes comments into various emotional categories, such as joy, anger, sadness, and more.

2. **Subscription and Daily Reports:** Users can effortlessly subscribe to specific YouTube videos using the Telegram bot. Once subscribed, users receive daily reports outlining the changes in emotional sentiments within the video's comment section. This provides valuable insights into audience engagement and sentiment shifts over time.

3. **Playlist Support:** The system goes beyond individual videos and extends its capabilities to entire playlists. Users can input a playlist URL, and the bot will automatically subscribe to all videos within the playlist. This feature enables a comprehensive analysis of the emotional journey across multiple videos.

4. **Data Visualization:** The generated emotional reports are not just data points; they are visually represented through intuitive diagrams and graphs. This empowers users to grasp emotional shifts at a glance, making it easy to identify trends and patterns in audience responses.

5. **User-Friendly Telegram Bot:** The project is accessible through a Telegram bot interface, making it user-friendly and convenient. With commands such as `/list`, `/start`, and `/help`,`/Unsubscribe`  users can seamlessly navigate the system and retrieve the information they need.

6. **Integration with Elasticsearch,Kibana and Kafka:** The backend infrastructure of the project is supported by Elasticsearch, Kibana and also Kafka. This combination enables efficient data storage, retrieval, and visualization, ensuring a robust and scalable platform for emotional analysis.

The **YouTube Videos Emotional Analyzer** project transcends conventional analytics by tapping into the emotional pulse of online communities. It bridges the gap between data and emotions, allowing content creators to adapt their strategies, marketers to refine their campaigns, and researchers to gain profound insights into human sentiment in the digital landscape.

By combining cutting-edge technologies, intuitive user experience, and powerful analytical capabilities, this project serves as a valuable tool for anyone seeking to decipher the intricate emotional responses sparked by YouTube videos.


<img width="888" alt="Screenshot 2023-08-26 at 20 49 29" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/6090903f-bcad-41fb-bfe7-6210763485bd">

## Prerequisites
Before using the system, ensure you complete the following prerequisites:

1. Configure the required fields in the configuration file.
2. Start your Elasticsearch and Kibana servers.
3. Start your Kafka server with Zookeeper.

## Telegram Commands
The Telegram bot supports the following commands:

- `/list`: Lists all the videos to which you've subscribed.
- `/start`: Initiates the bot.
- `/help`: Provides basic command information.

When the bot is started, it will prompt you to provide a video or playlist URL. If the URL corresponds to a video you are not subscribed to, the system fetches data from the beginning. If it's a subscribed video, the system generates a diagram immediately.

<img width="935" alt="Screenshot 2023-08-26 at 20 58 10" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/4d23d2d3-f755-4b1f-b525-862e4c8df52a">

The system also supports playlist URLs. When you provide a playlist URL, the bot subscribes to all videos within the playlist, updating emotion data instantly. Daily reports for subscribed videos are sent to users at 02:00.

## Getting Started
To start using the YouTube Videos Emotional Analyzer, follow these steps:

1. Configure the required fields in the configuration file.
2. Start your Elasticsearch, Kibana, and Kafka servers.
3. Initialize the Telegram bot and follow the provided commands.
4. Provide video or playlist URLs to the bot to start receiving emotional analysis reports.

## Screenshots
<img width="720" alt="Screenshot 2023-08-26 at 21 01 32" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/75e62889-34b2-403b-98e4-1b91444924f2">
<img width="368" alt="Screenshot 2023-08-26 at 21 00 34" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/94fac928-2937-4df7-b88b-f5e46fb95b75">


## Contributing
Contributions are welcome! If you encounter any issues or have ideas for improvement, please open an issue or pull request on the [GitHub repository](https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer).

## License
This project is licensed under the [MIT License](LICENSE).

---

*Note: Replace the placeholders in the content above with your actual project details and URLs.*
