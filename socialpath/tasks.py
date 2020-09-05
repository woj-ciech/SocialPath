from datetime import datetime
from backend import utilsy
import tweepy
import praw
from social.models import *
import json
from bs4 import BeautifulSoup
import requests


from celery import shared_task
from celery_progress.backend import ProgressRecorder

keys = utilsy.get_keys()
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}

@shared_task(bind=True)
def socialpath_main(self,name):

    progress_recorder = ProgressRecorder(self)
    total = len(functions_dict)
    result = 0
    for c,i in enumerate(functions_dict):
        functions_dict[i](name)
        result += c
        print(c)
        progress_recorder.set_progress(c + 1, total=total)
    # return result

def check_twitter(username):
    auth = tweepy.OAuthHandler(keys['keys']['twitter']["TWITTER_CONSUMER_KEY"], keys['keys']['twitter']["TWITTER_CONSUMER_SECRET"])
    auth.set_access_token(keys['keys']['twitter']['TWITTER_ACCESS_TOKEN'], keys['keys']['twitter']["TWITTER_ACCESS_TOKEN_SECRET"])

    # Create API object
    api = tweepy.API(auth)
    u = Usernames.objects.get(username=username)

    try:
        details = api.get_user(username)
        print('a')
        t = Twitt(user=username,exists=True,bio=details.description,created_at=details.created_at,profile_pic=details.profile_image_url,
                  screen_name=details.name, followers=details.followers_count, friends=details.friends_count)
        t.save()

        u.twitt = t

        u.save()
        utilsy.create_directory(username + "/twitter")

    except:
        ttt = api.search_users(username)
        similar = []
        for i in ttt:
            similar.append(i.screen_name)
        t = Twitt(user=username,exists=False, bio="Account does not exist",similar=similar)
        t.save()
        u.twitt = t
        u.save()

def check_facebook(username):
    req = requests.get("https://facebook.com/"+username, headers=headers)
    pic = ""
    u = Usernames.objects.get(username=username)
    if req.status_code == 200:

        soup = BeautifulSoup(req.content)

        for i in soup.find_all("img", {"class": "_11kf img"}):
            pic = i.attrs['src']

        f = Face(user=username,exists=True, profile_pic=pic)
        f.save()
        u.face = f
        u.save()

    else:
        f = Face(user=username,exists=False)
        f.save()
        u.face = f
        u.save()

def check_reddit( username ):
    reddit = praw.Reddit(client_id=keys['keys']['reddit']['CLIENT_ID'],
                         client_secret=keys['keys']['reddit']['CLIENT_SECRET'],
                         password=keys['keys']['reddit']['PASSWORD'],
                         user_agent=keys['keys']['reddit']['USER_AGENT'],
                         username=keys['keys']['reddit']['USERNAME'])
    u = Usernames.objects.get(username=username)

    try:
        a = reddit.redditor(username).comment_karma
        joined = datetime.utcfromtimestamp(reddit.redditor(username).created_utc).strftime('%Y-%m-%d %H:%M:%S')
        img = reddit.redditor(username).icon_img

        r = Redd(user=username,exists=True, joined = joined, profile_pic = img, karma = a)
        r.save()
        u.redd= r
        u.save()
        utilsy.create_directory(username + "/reddit")

    except:
        r = Redd(user=username,exists=False)
        r.save()
        u.redd = r
        u.save()

def check_stackoverflow(username):
    u = Usernames.objects.get(username=username)

    try:
        req = requests.get(
            "https://api.stackexchange.com/2.2/users?order=desc&inname=" + username + "&site=stackoverflow")
        req_json = json.loads(req.content)

        if req_json['items']:
            try:
                for item in req_json['items']:
                    print(item['display_name'] + "--" + username)
                    if item['display_name'] == username:
                        print('chuuuj')
                        if 'location' in item:
                            location = item['location']
                        else:
                            location = ""

                        if 'website_url' in item:
                            url = item['website_url']
                        else:
                            url = ""

                        s = Stackover(user=username, user_id=item['user_id'], exists=True, profile_pic=item['profile_image'],
                                      created_at=datetime.utcfromtimestamp(item['creation_date']).strftime(
                                          '%Y-%m-%d %H:%M:%S'),
                                      last_access=datetime.utcfromtimestamp(item['last_access_date']).strftime(
                                          '%Y-%m-%d %H:%M:%S'), reputation=item['reputation'], location=location, user_url=url,
                                      url=item['link'])
                        s.save()
                        u.stackover = s
                        u.save()
                        utilsy.create_directory(username + "/stackoverflow")
                        break
                    else:
                        pass

            except Exception as e:
                print(e)
        else:
            s = Stackover(user=username,exists=False)
            s.save()
            u.stackover = s
            u.save()
            utilsy.create_directory(username + "/stackoverflow")

    except:
        pass

def check_instagram(username):


    c = keys['keys']['instagram']['instagram_cookie']
    headers_insta = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
               "Cookie":c}

    endpoint = "https://www.instagram.com/" + username + "/?__a=1"
    req = requests.get(endpoint, headers=headers_insta)
    u = Usernames.objects.get(username=username)
    if req.status_code == 200:
        try:
            req_json = json.loads(req.content)
            bio = req_json['graphql']['user']['biography']
            bio_url = req_json['graphql']['user']['external_url']
            followers = req_json['graphql']['user']['edge_followed_by']['count']
            follow = req_json['graphql']['user']['edge_follow']['count']
            screen_name = req_json['graphql']['user']['full_name']
            profile_pic = req_json['graphql']['user']['profile_pic_url_hd']
            utilsy.create_directory(username + "/instagram")
            i = Insta(user=username,exists=True,bio=bio, bio_url=bio_url, followers=followers,follow=follow,screen_name=screen_name,
                      profile_pic=profile_pic)
            i.save()
            u.insta = i
            u.save()
        except:
            pass
    else:
        i = Insta(user=username,exists=False)
        i.save()
        u.insta = i
        u.save()

@shared_task(bind=True)
def instagram_timeline(self,username):
    u = Insta.objects.get(user=username)
    progress_recorder = ProgressRecorder(self)
    info = {"descriptions":[], "captions":[], 'locations':{},'timestamps':{}}
    counter = 0
    c = keys['keys']['instagram']['instagram_cookie']
    headers_insta = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Cookie": c}
    endpoint = "https://www.instagram.com/" + username + "/?__a=1"
    req = requests.get(endpoint, headers=headers_insta)
    req_json = json.loads(req.content)
    if req_json:
        total = req_json['graphql']['user']['edge_owner_to_timeline_media']['count']

        for item in req_json['graphql']['user']['edge_owner_to_timeline_media']['edges']:
            counter = counter + 1
            progress_recorder.set_progress(counter, total=total)
            self.update_state(state="PROGRESS",
                              meta={"percentage": counter / total * 100})
            try:
                info['descriptions'].append(item['node']['edge_media_to_caption']['edges'][0]['node']['text'])
            except:
                pass
            if 'taken_at_timestamp' in item['node']:
                info['timestamps'][datetime.utcfromtimestamp(item['node']['taken_at_timestamp']).strftime(
                    '%Y-%m-%d %H:%M:%S')] = "https://instagram.com/p/" + item['node']['shortcode']
            if 'location' in item['node']:
                if item['node']['location']:
                    info['locations'][item['node']['location']['name']] = "https://instagram.com/p/" + \
                                                                               item['node']['shortcode']

            try:
                info['captions'].append(item['node']['accessibility_caption'])
            except:
                pass

        has_more = req_json['graphql']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        end_cursor = req_json['graphql']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

        while has_more:
            next_req_endpoint = "https://www.instagram.com/graphql/query/?query_id=17888483320059182&id=" + str(
                req_json['graphql']['user']['id']) + "&first=12&after=" + end_cursor
            next_req = requests.get(next_req_endpoint)
            next_req_json = json.loads(next_req.content)

            try:
                for photo in next_req_json['data']['user']['edge_owner_to_timeline_media']['edges']:
                    counter = counter + 1
                    progress_recorder.set_progress(counter, total=total)
                    self.update_state(state="PROGRESS",
                                      meta={"percentage": counter / total * 100})

                    for desc in photo['node']['edge_media_to_caption']['edges']:
                        info['descriptions'].append(desc['node']['text'])


                    if 'taken_at_timestamp' in photo['node']:
                        info['timestamps'][
                            datetime.utcfromtimestamp(photo['node']['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')] = \
                            "https://instagram.com/p/" + photo['node']['shortcode']

                    if 'location' in photo['node']:
                        if photo['node']['location']:
                            info['locations'][photo['node']['location']['name']] = "https://instagram.com/p/" + \
                                                                                        photo['node']['shortcode']

                    try:
                        info['captions'].append(photo['node']['accessibility_caption'])
                    except:
                        pass

                has_more = next_req_json['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
                end_cursor = next_req_json['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            except:
                has_more = False
                u.locations = info['locations']
                u.save()
                hashtags = utilsy.count_hashtags(info['descriptions'], "")
                utilsy.savecsv(hashtags, "hashtags", username + "/instagram")
                words = utilsy.count_text(info['descriptions'])
                utilsy.savecsv(words, "words", username + "/instagram")
                utilsy.savecsv(info['timestamps'], "calendar", username + "/instagram")
                self.update_state(state="SUCCESS",
                                  meta={"OK": "OK"})
                # rate limit
        u.locations = info['locations']
        u.save()
        hashtags = utilsy.count_hashtags(info['descriptions'], "")
        utilsy.savecsv(hashtags, "hashtags", username + "/instagram")
        words = utilsy.count_text(info['descriptions'])
        utilsy.savecsv(words, "words", username + "/instagram")
        utilsy.savecsv(info['timestamps'], "calendar", username + "/instagram")
        self.update_state(state="SUCCESS",
                          meta={"OK": "OK"})
    else:
        pass

@shared_task(bind=True)
def reddit_timeline(self, username):
    u = Redd.objects.get(user=username)
    progress_recorder = ProgressRecorder(self)
    info = {"subreddits": [], "ups": {},
            "text": [], 'timestamps': {}}
    counter = 0
    reddit = praw.Reddit(client_id=keys['keys']['reddit']['CLIENT_ID'],
                         client_secret=keys['keys']['reddit']['CLIENT_SECRET'],
                         password=keys['keys']['reddit']['PASSWORD'],
                         user_agent=keys['keys']['reddit']['USER_AGENT'],
                         username=keys['keys']['reddit']['USERNAME'])

    subreddits = []

    try:

        info['karma'] = str(reddit.redditor(username).comment_karma)
    except:
        return False


    for comment in reddit.redditor(username).comments.new(limit=50):
        counter = counter + 1
        progress_recorder.set_progress(counter, total=50)
        self.update_state(state="PROGRESS",
                          meta={"percentage": counter / 50 * 100})
        info['text'].append(comment.body)
        info['timestamps'][datetime.utcfromtimestamp(comment.created).strftime(
            '%Y-%m-%d %H:%M:%S')] = "https://reddit.com" + comment.permalink
        subreddits.append(comment.subreddit_name_prefixed)
        info['ups'][comment.ups] = "https://reddit.com" + comment.permalink

    counter = 0
    for submission in reddit.redditor(username).submissions.new(limit=50):
        counter = counter + 1
        progress_recorder.set_progress(counter, total=50)
        self.update_state(state="PROGRESS",
                          meta={"percentage": counter / 50 * 100})
        info['text'].append(submission.selftext)
        info['timestamps'][datetime.utcfromtimestamp(submission.created).strftime(
            '%Y-%m-%d %H:%M:%S')] = "https://reddit.com" + submission.permalink
        subreddits.append(submission.subreddit_name_prefixed)
        info['ups'][submission.ups] = "https://reddit.com" + submission.permalink

    info['subreddits'] = utilsy.count_words(subreddits)
    if info['timestamps']:
        utilsy.savecsv(info['timestamps'], "calendar", username + "/reddit")

    if info['subreddits']:
        hashtags = utilsy.count_words(info['subreddits'])
        utilsy.savecsv(hashtags, "hashtags", username + "/reddit")

    if info['text']:
        words = utilsy.count_text(info['text'])
        utilsy.savecsv(words, "words", username + "/reddit")

    self.update_state(state="SUCCESS",
                      meta={"OK": "OK"})

def check_pinterest(username):
    endpoint = "https://www.pinterest.com/"+ username

    u = Usernames.objects.get(username=username)

    req = requests.get(endpoint, headers=headers)

    if req.status_code == 200:
        try:
            soup = BeautifulSoup(req.content)
            for i in soup.find_all("script", {"id": "initial-state"}):
                info_json = json.loads(i.contents[0])
            profile_pic = info_json['resourceResponses'][0]['response']['data']['user']['image_xlarge_url']
            url = info_json['resourceResponses'][0]['response']['data']['user']['domain_url']
            following = info_json['resourceResponses'][0]['response']['data']['user']['following_count']
            followers = info_json['resourceResponses'][0]['response']['data']['user']['follower_count']
            locale = info_json['resourceResponses'][0]['response']['data']['user']['locale']
            about = info_json['resourceResponses'][0]['response']['data']['user']['about']

            p = Pinterest(user=username,exists=True, profile_pic=profile_pic, url=url, following=following, followers=followers, locale=locale, about=about )
            p.save()
            u.pinterest = p
            u.save()
        except:
            pass
    else:
        p = Pinterest(user=username,exists=False)
        p.save()

@shared_task(bind=True)
def stackoverflow_timeline(self, username):
    u = Stackover.objects.get(user=username)
    progress_recorder = ProgressRecorder(self)
    info1 = {"score": {}, "tags": {}, "text": [], "timestamps": {}}

    page = 1
    has_more = True

    while has_more:
        req_tags = requests.get("https://api.stackexchange.com/2.2/users/" + u.user_id + "/tags?order=desc&sort=popular&site=stackoverflow&pagesize=100&page=" + str(
            page) + "&filter=!9WaZnBfu9")
        req_json_posts = json.loads(req_tags.content)
        progress_recorder.set_progress(page, total=50)
        self.update_state(state="PROGRESS",
                          meta={"percentage": page / 50 * 100})
        page = page + 1
        for tag in req_json_posts['items']:
            info1['tags'][tag['name']] = str(tag['count'])

        has_more = req_json_posts['has_more']

        if page == 20:
            break

    page = 1
    has_more = True

    while has_more:
        req_posts = requests.get("https://api.stackexchange.com/2.2/users/" + u.user_id + "/posts?order=desc&sort=activity&site=stackoverflow&pagesize=100&page=" + str(
            page) + "&filter=!3ykawIm9Sw9*3Q51G")
        req_json_posts = json.loads(req_posts.content)
        progress_recorder.set_progress(page, total=50)
        self.update_state(state="PROGRESS",
                          meta={"percentage": page / 50 * 100})
        page = page + 1
        for post in req_json_posts['items']:
            info1['text'].append(post['body_markdown'])
            info1['score'][post['score']] = post['link']
            info1['timestamps'][datetime.utcfromtimestamp(post['creation_date']).strftime('%Y-%m-%d %H:%M:%S')] = post[
                'link']

        has_more = req_json_posts['has_more']

        if page == 20:
            break

    utilsy.savecsv(info1['timestamps'], "calendar", username + "/stackoverflow")
    utilsy.savecsv(info1['tags'], "hashtags", username + "/stackoverflow")
    words = utilsy.count_text(info1['text'])
    utilsy.savecsv(words, "words", username + "/stackoverflow")
    self.update_state(state="SUCCESS",
                      meta={"OK": "OK"})

@shared_task(bind=True)
def twitter_timeline(self, username):
    u = Twitt.objects.get(user=username)
    progress_recorder = ProgressRecorder(self)
    counter = 0
    auth = tweepy.OAuthHandler(keys['keys']['twitter']["TWITTER_CONSUMER_KEY"],
                               keys['keys']['twitter']["TWITTER_CONSUMER_SECRET"])
    auth.set_access_token(keys['keys']['twitter']['TWITTER_ACCESS_TOKEN'],
                          keys['keys']['twitter']["TWITTER_ACCESS_TOKEN_SECRET"])

    # Create API object
    api = tweepy.API(auth)
    info = {"hashtags": [], "symbols": [], "user_mentions": {}, "urls": [], "text": [],
            "timestamps": {}, "geo": []}

    try:
        for status in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended").items():
            if counter == 20:
                counter = 0
                progress_recorder.set_progress(counter, total=20)
                self.update_state(state="PROGRESS",
                                  meta={"percentage": counter / 20 * 100})
            counter = counter + 1
            progress_recorder.set_progress(counter, total=20)
            self.update_state(state="PROGRESS",
                              meta={"percentage": counter / 20 * 100})
            try:
                for hashtag in status.entities['hashtags']:
                    info['hashtags'].append("#" + hashtag['text'])

                for mentions in status.entities['user_mentions']:
                    if mentions['screen_name'] not in info['user_mentions']:
                        info['user_mentions'][mentions[
                            'screen_name']] = "https://twitter.com/" + username + "/status/" + status.id_str

                for url in status.entities['urls']:
                    info['urls'].append(url['expanded_url'])

                if not status.full_text.startswith("RT"):
                    info['text'].append(status.full_text)
                info['timestamps'][status.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S")] = "https://twitter.com/" + username + "/status/" + status.id_str
            except:
                pass

        utilsy.savecsv(info['timestamps'], "calendar", username + "/twitter")
        hashtags = utilsy.count_hashtags(info['hashtags'], 'twitter')
        utilsy.savecsv(hashtags, "hashtags", username + "/twitter")
        words = utilsy.count_text(info['text'])
        utilsy.savecsv(words, "words", username + "/twitter")
        self.update_state(state="SUCCESS",
                          meta={"OK": "OK"})
    except:
        pass

def check_github(username):
    end = "https://api.github.com/users/" + username
    u = Usernames.objects.get(username=username)
    req = requests.get(end)

    if req.status_code == 200:
        req_json = json.loads(req.content)
        profile_pic = req_json['avatar_url']
        blog = req_json['blog']
        location = req_json['location']
        email = req_json['email']
        bio = req_json['bio']
        twitter_username = req_json['twitter_username']
        repos = req_json['public_repos']
        followers = req_json['followers']
        following = req_json['following']
        created_at = req_json['created_at']
        g = Github(user=username,exists=True, profile_pic=profile_pic, blog=blog, location=location, email=email,bio=bio,
                   twitter_username=twitter_username, repos=repos, followers=followers, following=following,
                   created_at=created_at)
        g.save()
        u.github = g
        u.save()

    else:
        g = Github(user=username,exists=False)
        g.save()
        u.github = g
        u.save()

def check_tumblr(username):
    end = "https://"+username+".tumblr.com"
    u = Usernames.objects.get(username=username)
    try:
        req = requests.get(end)
        image = "/static/images/socialpath.png"
        title = ""
        if req.status_code == 200:
            soup = BeautifulSoup(req.content)
            for i in soup.find_all("a", {"class": "user-avatar"}):
                image = i.attrs['style'].split("(")[1][:-1]
            for i in soup.find_all(('h1', {"class": "blog-title"})):
                title = str(i.text)

            print(image)
            print(title)
            t = Tumblr(user=username,exists=True, profile_pic = image, title=title)
            t.save()
            u.tumblr = t
            u.save()
        else:
            t = Tumblr(user=username,exists=False)
            t.save()
            u.tumblr = t
            u.save()
    except:
        pass

def check_steam(username):
    end = "https://steamcommunity.com/id/" + username

    u = Usernames.objects.get(username=username)

    req = requests.get(end)
    real_name = ""
    location= ""
    profile_pic = "/static/images/socialpath.png"
    if req.status_code == 200:
        soup = BeautifulSoup(req.content)
        try:
            im = soup.find("div", {"class": "profile_avatar_frame"})
            if im:
                profile_pic1 = im.parent.contents[3].attrs['src']
            else:
                im2 = soup.find("div", {"class": "playerAvatarAutoSizeInner"})
                profile_pic2 = im2.contents[1].attrs['src']
                profile_pic1 = None

            for i in soup.find_all('div', {"class": "header_real_name ellipsis"}):
                if i.contents[1].contents:
                    real_name = str(i.contents[1].contents[0])
            for i in soup.find_all('img', {"class": "profile_flag"}):
                location = i.next.rstrip().lstrip()
            l = soup.find('span', {"class": "friendPlayerLevelNum"})
            level = str(l.contents[0])

            if profile_pic1:
                profile_pic = profile_pic1
            if profile_pic2:
                profile_pic = profile_pic2

            print(profile_pic)
            s = Steam(user=username,exists=True, profile_pic=profile_pic, real_name= real_name, location=location, level=level)
            s.save()
            u.steam = s
            u.save()
        except Exception as e:
            print(e)
    else:
        s = Steam(user=username,exists=False)
        s.save()
        u.steam = s
        u.save()

def check_pastebin(username):
    end = "https://pastebin.com/u/" + username

    req = requests.get(end)

    u = Usernames.objects.get(username=username)

    if req.status_code == 200:
        soup = BeautifulSoup(req.content)

        im = soup.find("div", {"class": "user-icon"})
        image = "https://pastebin.com" + im.contents[1].attrs['src']
        v = soup.find('span', {"class": "views"})
        views = str(v.contents[0])
        for i in soup.find_all('span', {"class": "views -all"}):
            paste_views = i.next.rstrip().lstrip()
        for i in soup.find_all('span', {"class": "date-text"}):
            joined = i.attrs['title']

        p = Paste(user=username,exists=True, profile_pic = image, views=views,paste_views=paste_views, joined=joined)
        p.save()
        u.paste = p
        u.save()

    else:
        p = Paste(user=username,exists=False)
        p.save()
        u.paste = p
        u.save()

functions_dict = {'pastebin':check_pastebin,"steam":check_steam,"tumblr":check_tumblr,"github":check_github,"pinterest":check_pinterest,"instagram":check_instagram,"reddit": check_reddit, 'twitter':check_twitter, "stackoverflow":check_stackoverflow, 'facebook':check_facebook}
