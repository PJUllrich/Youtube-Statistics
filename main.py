import isodate
from datetime import timedelta
from functions import *
from spinner import *
import sys

spinner = Spinner()
spinner.start()

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

spinner.stop()
print("The total playtime of the selected videos is: " + t)


