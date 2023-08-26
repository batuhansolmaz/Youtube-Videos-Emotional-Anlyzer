# Youtube-Videos-Emotional-Anlyzer

#Aim of the project.
This project makes you available to analyze Youtube videos comments emotional datas. When user gives a url to telegram bot user automatically subscribes to that video and will receive comparative 
results daily. System fethc all data subscribed video datas from youtube daily and compares with the previous data and reports to user automatically with the detailed explanation of changed emotions 
. User can unsubscribe from video via /Unsubscribe command.
##Prerequisites
You need to specify required fields in config file. 
Then you should start your elasticsearch and kibana servers. You should also start your kafka server with zookeper.
After that you are ready to go.
<img width="888" alt="Screenshot 2023-08-26 at 20 49 29" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/6090903f-bcad-41fb-bfe7-6210763485bd">


##Telegram commands
1-) /list
this lists all the videos that you subscribed
<img width="720" alt="Screenshot 2023-08-26 at 21 01 32" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/75e62889-34b2-403b-98e4-1b91444924f2">


2-) /start
starts the bot
3-) /help 
basic help commmand


When bot starts it will ask you to provide video or playlist url. When you provide a url it will check if that video is already subscribed video or not if not then it 
will fetch the data from beggining else it will generate the diagram immediatly.

<img width="935" alt="Screenshot 2023-08-26 at 20 58 10" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/4d23d2d3-f755-4b1f-b525-862e4c8df52a">


You can also give playlist url not just a video url. When user enters a playlist url it automatically subscribes all the video datas in the playlist and will retrain all the emotion datas instantly

also system will report all the subscribed video datas to user at 02.00 at every day.

<img width="368" alt="Screenshot 2023-08-26 at 21 00 34" src="https://github.com/batuhansolmaz/Youtube-Videos-Emotional-Anlyzer/assets/108425372/94fac928-2937-4df7-b88b-f5e46fb95b75">

