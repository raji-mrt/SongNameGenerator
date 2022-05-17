import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import json
import re
import dictionary


def get_track_names(genre, limit):
    category = genre
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    track_names = []
    counter = 0
    # latin = 0JQ5DAqbMKFxXaXKP7zcDp
    # regional_mexican = 0JQ5DAqbMKFDTEtSaS4R92
    # arab = 0JQ5DAqbMKFQ1UFISXj59F
    if genre in ('desi', 'latin', 'regional_mexican', 'arab', 'rnb'):
        print("+++These genres will not use dictionary")
        playlist_id = ""
        if genre == 'desi':
            response = spotify.category_playlists(category, 'US', 1, random.randint(0, 9))
            print(response)
            playlist_id = response['playlists']['items'][0]['id']
            response = spotify.playlist_items(playlist_id, 'items(track(name))')
        elif genre == 'latin':
            latin_playlists = ["37i9dQZF1DWY7IeIP1cdjF", "37i9dQZF1DWXmQEAjlxGhi", "37i9dQZF1DX10zKzsJ2jva", "37i9dQZF1DWZJIhAWlsiOv",
                               "37i9dQZF1DX7cmFV9rWM0u", "37i9dQZF1DX7HGyCQ2dcNx", "37i9dQZF1DX1hVRardJ30X", "37i9dQZF1DX5AVYhCeISA6",
                               "37i9dQZF1DXbvzw24ukZEU", "37i9dQZF1DXbLRILp4Jb3D"]
            playlist_id = random.choice(latin_playlists)
        elif genre == 'regional_mexican':
            regional_mexican_playlists = ["37i9dQZF1DX905zIRtblN3", "37i9dQZF1DXb0COFso7q0D", "37i9dQZF1DX2shzuwwKw0y", "37i9dQZF1DWZQGZ7yvpH00"]
            playlist_id = random.choice(regional_mexican_playlists)
        elif genre == 'arab':
            arab_playlists = ["37i9dQZF1DX5cO1uP1XC1g", "37i9dQZF1DXd3AhRYJnfcl", "37i9dQZF1DWYHO8PTSQ9fM", "37i9dQZF1DXe3aCmUoBd8n",
                              "37i9dQZF1DX657Vh1lw2BF", "37i9dQZF1DX4qF0846GNk8", "37i9dQZF1DWTZ8jTY8g4MU", "37i9dQZF1DWU486KSiznWZ",
                              "37i9dQZF1DXaL8gtxi9eun", "37i9dQZF1DX0UetYTdFoTk"]
            playlist_id = random.choice(arab_playlists)
        elif genre == 'rnb':
            rnb_playlists = ["37i9dQZF1DX9XIFQuFvzM4", "37i9dQZF1DX4SBhb3fqCJd", "37i9dQZF1DX0QKpU3cGsyb", "37i9dQZF1DWYmmr74INQlb",
                              "37i9dQZF1DX62Nfha2yFhL", "37i9dQZF1DX6VDO8a6cQME", "37i9dQZF1DWXbttAJcbphz", "37i9dQZF1DX4y8h9WqDPAE",
                              "37i9dQZF1DXaXDsfv6nvZ5", "37i9dQZF1DX2PG4mbkilf3"]
            playlist_id = random.choice(rnb_playlists)
        response = spotify.playlist_items(playlist_id, 'items(track(name))')
        random.shuffle(response['items'])
        for elements in response['items']:
            track_name = elements['track']['name']
            if track_name.count(" ") > 1:
                print("+++Track name contains more than two words")
                continue
            if not re.match('[a-zA-Z\s]+$', track_name):
                print("+++Track name contains special characters")
                continue
            counter = counter + 1
            track_names.append(elements['track']['name'])
            if counter == limit:
                break
    else:
        response = spotify.category_playlists(category, 'US', 1, random.randint(0, 9))
        print(response)
        playlist_id = response['playlists']['items'][0]['id']
        response = spotify.playlist_items(playlist_id, 'items(track(name))')
        random.shuffle(response['items'])
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
                if counter == limit:
                    break

    print(track_names)
    return track_names


def lambda_handler(event, context):
    genre = event["queryStringParameters"]['genre']
    limit = int(event['queryStringParameters'].get('limit', '10'))

    track_names = get_track_names(genre, limit)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(track_names)
    }
