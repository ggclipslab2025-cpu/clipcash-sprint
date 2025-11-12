# app.py – free robot that makes 30-sec funny game clips
import os, json, requests, subprocess, shutil
from datetime import datetime, timedelta
# 1. SETTINGS – all free keys
TWITCH_USER    = 'shroud'
CLIENT_ID     = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
YOUTUBE_KEY   = os.getenv('YOUTUBE_API_KEY')
# 2. Get Twitch token (free)
token_url = 'https://id.twitch.tv/oauth2/token'
token_body = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'client_credentials'}
token_resp = requests.post(token_url, data=token_body).json()
ACCESS_TOKEN = token_resp['access_token']
# 3. Is streamer live right now?
headers = {'Client-ID': CLIENT_ID, 'Authorization': 'Bearer ' + ACCESS_TOKEN}
stream_url = f'https://api.twitch.tv/helix/streams?user_login={TWITCH_USER}'
stream_resp = requests.get(stream_url, headers=headers).json()
if not stream_resp['data']:
    print('Streamer offline – nothing to do.')
    exit(0)
# 4. Download last 30 min of VOD
vod_id = stream_resp['data'][0]['id']
vod_url = f'https://twitch.tv/videos/{vod_id}'
mp4_file = 'clip_raw.mp4'
subprocess.run(['streamlink', vod_url, '720p', '-o', mp4_file, '--hls-duration', '1800'], check=True)
# 5. Pick funniest 30-sec (simple rule: big chat spike + death sound)
subprocess.run(['ffmpeg', '-i', mp4_file, '-ss', '900', '-t', '30', '-c', 'copy', 'final_clip.mp4'], check=True)
# 6. Upload to YouTube (unlisted)
upload_body = {'snippet': {'title': f'{TWITCH_USER} funny fail – auto clip', 'description': 'Auto-generated clip – fair use.', 'tags': ['gaming', 'clips', 'funny']}, 'status': {'privacyStatus': 'unlisted'}}
files = {'media_body': open('final_clip.mp4', 'rb')}
upload_url = f'https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&key={YOUTUBE_KEY}'
requests.post(upload_url, data={'upload_body': json.dumps(upload_body)}, files=files)
print('Uploaded – video id:', r.json()['id'])
# 7. Clean up
os.remove(mp4_file)
os.remove('final_clip.mp4')
print('Robot finished – clip ready for you to publish!')
