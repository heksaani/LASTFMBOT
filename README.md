# LASTFM Telegram bot

This is a simple Telegram bot that uses the [Last.fm API](https://www.last.fm/api) to get information about the music you have listened to.

# Current features
/monthartist - prints out the top 10 artists you have listened to during the last 30 days and the number of scrobbles

/monthtrack - prints out the top 10 tracks you have listened to during the last 30 days and the number of scrobbles 

/weekartist - prints out the top 10 artists you have listened to during the last 7 days and the number of scrobbles

/weektrack - prints out the top 10 tracks you have listened to during the last 7 days and the number of scrobbles 

## How to use

1. Clone the repository

```bash
git clone https://github.com/heksaani/LASTFMBOT.git
```

2. Create a `.env` file in the root directory with the following content:

```bash
LASTFM_API_KEY=YOUR_LASTFM_API_KEY
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
LASTFM_USERNAME=YOUR_LASTFM_USERNAME
```

Instructions on how to obtain the API key and the bot token : 

[LASTFM](https://www.last.fm/api/account/create) <br>
[TELEGRAM](https://core.telegram.org/bots#botfather)

3. Using the Dockerfile

```bash
docker build -t lastfmbot .
docker run -d --name lastfmbot lastfmbot
```
