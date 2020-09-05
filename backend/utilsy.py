from collections import Counter
import os
from itertools import islice
import json


def get_keys():
    with open("backend/keys.json","r") as keys:
        json_keys = json.loads(keys.read())

        return json_keys


def count_words(string_list):
    return Counter(string_list)

def create_directory(name):
    try:
        os.mkdir("social/static/"+name)
    except FileExistsError:
        pass

def count_text(text_list):
    splitted_text = []
    for text in text_list:
        splitted = text.split(" ")
        for split in splitted:
            if "#" not in split and split != "" and split != "," and split != ".":
                if "," in split:
                    split = split.replace(",","")
                    splitted_text.append(split)
                else:
                    splitted_text.append(split)

    if len(splitted_text) > 500:
        lengths = Counter()
        lengths.update(dict(islice(Counter(splitted_text).items(),500)))
        return lengths
    else:
        return Counter(splitted_text)

def count_hashtags(string_list, social):
    if social == "twitter":
        return Counter(string_list)

    hashtags = []
    for i in string_list:
        splitted = i.split(" ")
        for j in splitted:
            if j.rstrip().startswith('#'):
                hashtags.append(j)
                # else:
                #     hashtags.append(j)
    return Counter(hashtags)

def savecsv(list_to_save, name, username):
    with open("social/static/"+username+"/"+name + '.csv', 'w') as file:
        if name == 'calendar':
            file.write('day,link\n')
        if name == "hashtags":
            file.write('hashtag,count\n')
        if name == "words":
            file.write('word,count\n')

        for i in list_to_save:
            file.write(i + "," + str(list_to_save[i]) + "\n")