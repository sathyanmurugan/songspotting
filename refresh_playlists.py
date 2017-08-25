import spotipy
import util
import psycopg2
import psycopg2.extras
import os
from random import shuffle 

#Get list of playlists to be updated from the DB
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) 
sql = """
SELECT
     p.user_id
    ,p.playlist_id
    ,p.playlist_seed
    ,p.seed_attributes
    ,t.refresh_token

FROM user_playlists p
JOIN user_refresh_token t
  ON t.user_id = p.user_id 
"""
cursor.execute(sql)
results = cursor.fetchall()

#Initilize Auth Class
auth = util.AuthUser()

#For each playlist, refresh the content 
for r in results:
	try:
		token_data = auth.refresh_token(r['refresh_token']) #get access token
		sp = spotipy.Spotify(auth=token_data['access_token']) #connect to Spotify

		#Check if user still has this playlist on profile, else remove from database
		all_user_playlists = util.get_user_playlist_ids(token_data['access_token'])
		if r['playlist_id'] not in all_user_playlists:
			cursor.execute("DELETE FROM user_playlists WHERE playlist_id='{}'".format(r['playlist_id']))
			conn.commit()
			continue

		recommendation_ids = None

		if r['playlist_seed'] == 'favorite_tracks':
			results = sp.current_user_top_tracks(limit=20, time_range=r['seed_attributes'])
			result_ids = [result['id'] for result in results['items']]
			shuffle(result_ids)
			if len(result_ids) > 0:
				recommendations = sp.recommendations(seed_tracks=result_ids[0:5],limit=50)
				recommendation_ids = [track['id'] for track in recommendations['tracks']]

		elif r['playlist_seed'] == 'favorite_artists':
			results = sp.current_user_top_artists(limit=20, time_range=r['seed_attributes'])
			result_ids = [result['id'] for result in results['items']]
			shuffle(result_ids)
			if len(result_ids) > 0:
				recommendations = sp.recommendations(seed_artists=result_ids[0:5],limit=50)
				recommendation_ids = [track['id'] for track in recommendations['tracks']]

		elif r['playlist_seed'] == 'genre':
			recommendations = sp.recommendations(seed_genres=[r['seed_attributes']],limit=50)
			recommendation_ids = [track['id'] for track in recommendations['tracks']]

		elif r['playlist_seed'] == 'playlist':
			tracks = util.get_tracks_in_playlist(token_data['access_token'],r['user_id'],r['seed_attributes'])
			shuffle(tracks)
			if len(tracks) > 0:
				recommendations = sp.recommendations(seed_tracks=tracks[0:5],limit=50)
				recommendation_ids = [track['id'] for track in recommendations['tracks']]				

		if recommendation_ids:
			response = sp.user_playlist_replace_tracks(r['user_id'],r['playlist_id'],recommendation_ids)

	except Exception as e:
		print(str(e))

cursor.close()
conn.close()