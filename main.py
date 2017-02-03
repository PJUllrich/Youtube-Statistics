import sys
import requests
import configparser
import os
import json

cSec = 'GoogleApi'

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config/config.ini'
config = configparser.ConfigParser()
config.read(confPath)

def cget(section, name):
    """Returns a value with a given name from the configuration file."""
    return config[section][name]

# Read in the channel and optionally the playlist name
channel = sys.argv[1]
if len(sys.argv) == 3:
    playlist = sys.argv[2]

# Retrieve Channel ID
param = {'key': cget(cSec, 'Key'), 'part': 'id', 'forUsername': channel}
response = requests.get(cget(cSec, 'ChannelAccess'), params=param)
out = json.loads(response.text)

if len(out['items']) == 0:
    print('No Youtube Channel with the name ' + channel + ' could be found.')
    exit()

# Retrieve Playlist ID
channelId = out['items'][0]['id']
param = {'key': cget(cSec, 'Key'), 'part': 'id, snippet', 'channelId': channelId}
response = requests.get(cget(cSec, 'PlaylistAccess'), params=param)
out = json.loads(response.text)

if len(out['items']) == 0:
    print('No Playlist with the name ' + playlist + ' could be found.')
    exit()

for item in out['items']:
    if item['snippet']['title'] == playlist:
        playlistId = item['id']
        break

# Retrieve all Video IDs for the Playlist ID


