import sys
import requests
import configparser
import os
import json
import isodate
from datetime import timedelta

cSec = 'GoogleApi'

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config/config.ini'
config = configparser.ConfigParser()
config.read(confPath)


def cget(section, name):
    """Returns a value with a given name from the configuration file.
    """
    return config[section][name]


def get_channel_id(name):
    """Returns Youtube's ID for a channel with a given name.
    Only one ID is returned as it is assumed that Youtube channels
    have to have a unique name. Therefore, only one channel should be found
    """
    param = {'key': cget(cSec, 'Key'), 'part': 'id', 'forUsername': name}
    response = requests.get(cget(cSec, 'ChannelAccess'), params=param)
    out = json.loads(response.text)['items']

    if len(out) == 0:
        print('No Youtube Channel with the name ' + name + ' could be found.')
        exit()

    return out[0]['id']


def get_playlists_for_channel(id):
    """Returns all playlists of a given channel id
    """
    param = {'key': cget(cSec, 'Key'), 'part': 'id, snippet', 'channelId': id}
    response = requests.get(cget(cSec, 'PlaylistAccess'), params=param)
    return json.loads(response.text)['items']


def get_uploads_list(id):
    """Returns the ID of the Uploads playlist of a channel.
    """
    param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'id': id}
    response = requests.get(cget(cSec, 'ChannelAccess'), params=param)
    return json.loads(response.text)['items'][0]['contentDetails']['relatedPlaylists']['uploads']


def get_playlist_from_list(name, id):
    """Returns a specific playlist from a list of playlists
    """
    __list = get_playlists_for_channel(id)
    for i in __list:
        if i['snippet']['title'].lower() == name:
            return [i['id']]

    print('No Playlist with the name ' + name + ' could be found.')
    exit()


def get_all_playlist_ids_from_list(list):
    """Returns all IDs of all playlists in a given list.
    """
    out = []
    for i in list:
        out.append(i['id'])
    return out


def get_video_ids_for_playlist(id):
    """Returns all IDs of all video items in a given list.
    """
    num = int(cget(cSec, 'maxResults'))
    param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'playlistId': id, 'maxResults': num}
    response = requests.get(cget(cSec, 'PlaylistItemsAccess'), params=param)
    out = json.loads(response.text)

    items = out['items']
    total = int(out['pageInfo']['totalResults'])

    if total > num:
        fetched = num
        while fetched < total:
            param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'playlistId': id, 'maxResults': num,
                     'pageToken': out['nextPageToken']}
            response = requests.get(cget(cSec, 'PlaylistItemsAccess'), params=param)
            out = json.loads(response.text)
            items.extend(out['items'])
            fetched += num

    return items


def get_video_data_from_ids(id):
    """Retrieves and returns the data of a list of video IDs.
    """
    data = []
    fetched = 0
    num = int(cget(cSec, 'maxResults'))
    while fetched < len(id):
        idx_end = fetched + num if fetched + num < len(id) else len(id)
        param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'id': ", ".join(id[fetched:idx_end])}
        response = requests.get(cget(cSec, 'VideoAccess'), params=param)
        data.extend(json.loads(response.text)['items'])
        fetched += num

    return data


# Read in the channel and optionally the playlist name
ch = sys.argv[1].lower()
pl = ''
if len(sys.argv) == 3:
    pl = sys.argv[2].lower()


# Retrieve the channel ID
ch_id = get_channel_id(ch)


# Retrieve Playlist ID
if pl != '':
    pl_id = get_playlist_from_list(pl, ch_id)
else:
    pl_id = get_uploads_list(ch_id)


# Retrieve all Video IDs for the Playlist ID
v_item = get_video_ids_for_playlist(pl_id)


# Retrieve the video data for every video
v_id = []
for item in v_item:
    v_id.append(item['contentDetails']['videoId'])

v_data = get_video_data_from_ids(v_id)


# Add the durations of the videos together
dur = timedelta()
for v in v_data:
    dur += isodate.parse_duration(v['contentDetails']['duration'])

m, s = divmod(dur.total_seconds(), 60)
h, m = divmod(m, 60)
t = "%d Hours, %02d Minutes, and %02d Seconds" % (h, m, s)

print("The total playtime of the selected videos is: " + t)

