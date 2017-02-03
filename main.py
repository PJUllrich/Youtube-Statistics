import sys
import requests
import configparser
import os
import json
import isodate
from datetime import timedelta
import math

cSec = 'GoogleApi'

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config/config.ini'
config = configparser.ConfigParser()
config.read(confPath)

def cget(section, name):
    """Returns a value with a given name from the configuration file."""
    return config[section][name]

# Read in the channel and optionally the playlist name
channel = sys.argv[1].lower()
if len(sys.argv) == 3:
    playlist = sys.argv[2].lower()

# Retrieve Channel ID
param = {'key': cget(cSec, 'Key'), 'part': 'id', 'forUsername': channel}
response = requests.get(cget(cSec, 'ChannelAccess'), params=param)
out = json.loads(response.text)

if len(out['items']) == 0:
    print('No Youtube Channel with the name ' + channel + ' could be found.')
    exit()

channelId = out['items'][0]['id']

# Retrieve Playlist ID
param = {'key': cget(cSec, 'Key'), 'part': 'id, snippet', 'channelId': channelId}
response = requests.get(cget(cSec, 'PlaylistAccess'), params=param)
out = json.loads(response.text)

if len(out['items']) == 0:
    print('No Playlist with the name ' + playlist + ' could be found.')
    exit()

for item in out['items']:
    if item['snippet']['title'].lower() == playlist:
        playlistId = item['id']
        break

# Retrieve all Video IDs for the Playlist ID
maxResults = int(cget(cSec, 'maxResults'))
param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'playlistId': playlistId, 'maxResults': maxResults}
response = requests.get(cget(cSec, 'PlaylistItemsAccess'), params=param)
out = json.loads(response.text)

videoItems = out['items']
totalResults = int(out['pageInfo']['totalResults'])

if totalResults > maxResults:
    resultsFetched = maxResults
    while resultsFetched < totalResults:
        param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'playlistId': playlistId, 'maxResults': maxResults, 'pageToken': out['nextPageToken']}
        response = requests.get(cget(cSec, 'PlaylistItemsAccess'), params=param)
        out = json.loads(response.text)
        videoItems.extend(out['items'])
        resultsFetched += maxResults

# Retrieve the video data for every video
videoId = []
for item in videoItems:
    videoId.append(item['contentDetails']['videoId'])

videoData = []
resultsFetched = 0
while resultsFetched < totalResults:
    endIndex = resultsFetched + maxResults if resultsFetched + maxResults < totalResults else totalResults
    param = {'key': cget(cSec, 'Key'), 'part': 'contentDetails', 'id': ", ".join(videoId[resultsFetched:endIndex])}
    response = requests.get(cget(cSec, 'VideoAccess'), params=param)
    videoData.extend(json.loads(response.text)['items'])
    resultsFetched += maxResults

# Add the durations of the videos together
totalDuration = timedelta()
for video in videoData:
    totalDuration += isodate.parse_duration(video['contentDetails']['duration'])

m, s = divmod(totalDuration.total_seconds(), 60)
h, m = divmod(m, 60)
totalTime = "%d Hours, %02d Minutes, and %02d Seconds" % (h, m, s)

print("The total playtime of the selected videos is: " + totalTime)

