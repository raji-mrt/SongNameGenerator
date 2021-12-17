import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import json
import re
import dictionary


def get_track_names(genre):
    category = genre
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    response = spotify.category_playlists(category, 'US', 1, random.randint(0, 9))
    playlist_id = response['playlists']['items'][0]['id']
    response = spotify.playlist_items(playlist_id, 'items(track(name))')
    random.shuffle(response['items'])
    track_names = []
    counter = 0

    for elements in response['items']:
        track_name = elements['track']['name']
        if track_name.count(" ") > 1:
            print("+++Track name contains more than two words")
            continue
        if not re.match('[a-zA-Z\s]+$', track_name):
            print("+++Track name contains special characters")
            continue
        print("+++Valid Track name for processing : " + track_name)
        track_name_after_change = ''
        for word in track_name.split():
            modified_word = dictionary.get_close_word(word)
            if modified_word:
                print('++++++Modified by dictionary from ' + word + ' to ' + modified_word)
                track_name_after_change = track_name_after_change + ' ' + modified_word
            else:
                print('++++++Dictionary cannot modified this word')
                break
        print('+++New Track Name ' + track_name_after_change)
        if track_name_after_change:
            counter = counter + 1
            track_names.append(track_name_after_change[1:])
            if counter == 10:
                break

    print(track_names)
    return track_names


def lambda_handler(event, context):
    genre = event["queryStringParameters"]['genre']
    track_names = get_track_names(genre)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(track_names)
    }

