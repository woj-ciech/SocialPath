# SocialPath
<img src="https://www.offensiveosint.io/content/images/2020/07/OffensiveOsint-logo-RGB-2.png" width="300">

![](https://imgur.com/daYzPlO.jpg)

Track users across social media platforms

[Deanonymizing darknet users by username reuse](https://www.offensiveosint.io/socialpath-track-users-across-social-media-platforms/)

Research no. 2 in progress

Supported services:
- Facebook
- Twitter + details
- Stackoverflow + details
- Instagram + details
- Reddit + details
- Steam
- Pinterest
- Tumblr
- Pastebin
- Github

Requirements:
- Django
- Tweepy
- PRAW
- Celery
- Redis

# Install
Paste your API keys into [backend/keys.json](https://github.com/woj-ciech/SocialPath/blob/master/backend/keys.json) Remember to escape double quotes (") in instagram cookie with \ in json
```
pip3 install -r requirements.txt

apt-get install redis-server
redis-server
```
In new window in main directory
```
python3 manage.py makemigrations social
python3 manage.py migrate social
python3 manage.py migrate
python3 manage.py runserver
```
In new window in main directory
```
celery worker -A socialpath --loglevel=debug
```
After that SocialPath will be accessible at localhost:8000/search

Directory is created for each user with csv inside under /static/, for visualizations.

# Screens
![](https://imgur.com/q7JwZWH.jpg)
![](https://imgur.com/YikqzMA.jpg)
![](https://i.imgur.com/6OoSC09.png)
![](https://i.imgur.com/E1sFk7G.png)
![](https://imgur.com/AkffJES.jpg)
![](https://imgur.com/eu3d5xt.jpg)
![](https://i.imgur.com/yc9Mb9C.png)

