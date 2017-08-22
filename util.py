import os
import spotipy.oauth2 as oauth2
import time, datetime
import spotipy
from random import shuffle


SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = os.environ['SPOTIFY_REDIRECT_URI']
SPOTIFY_SCOPE = """
playlist-modify-public
playlist-modify-private
user-read-email
user-top-read
playlist-read-private
"""

def get_user_id(token_data):
	sp = spotipy.Spotify(auth=token_data['access_token']) 
	return sp.current_user()['id']


def store_refresh_token(token_data,db,table):

	#Check if user exists in dB
	user_id = get_user_id(token_data)
	user = table.query.filter_by(user_id=user_id).first()

	if user is None:
		#Add user and refresh_token
		now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		row = table(user_id,token_data['refresh_token'],now)
		db.session.add(row)
	else:
		#update refresh_token
		user.refresh_token = token_data['refresh_token']

	db.session.commit()
	return user_id

def create_playlist(token_data,db,table,**kwargs):
	sp = spotipy.Spotify(auth=token_data['access_token']) 
	response = sp.user_playlist_create(kwargs['user_id'],kwargs['playlist_name'])
	playlist_id = response['id']
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	#Add playlist details to database
	row = table(kwargs['user_id'],playlist_id,kwargs['playlist_name'],kwargs['playlist_seed'],kwargs['seed_attributes'],now)
	db.session.add(row)
	db.session.commit()
	return playlist_id


def reload_playlist(token_data,table,user_id,playlist_id):
	sp = spotipy.Spotify(auth=token_data['access_token'])

	playlist = table.query.filter_by(playlist_id=playlist_id).first()
	if playlist is None:
		return

	if playlist.playlist_seed == 'favorite_tracks':
		results = sp.current_user_top_tracks(limit=20, time_range=playlist.seed_attributes)
		result_ids = [result['id'] for result in results['items']]
		shuffle(result_ids)
		recommendations = sp.recommendations(seed_tracks=result_ids[0:5],limit=20)
		recommendation_ids = [track['id'] for track in recommendations['tracks']]
	

	elif playlist.playlist_seed == 'favorite_artists':
		results = sp.current_user_top_artists(limit=20, time_range=playlist.seed_attributes)
		result_ids = [result['id'] for result in results['items']]
		shuffle(result_ids)
		recommendations = sp.recommendations(seed_artists=result_ids[0:5],limit=20)
		recommendation_ids = [track['id'] for track in recommendations['tracks']]

	sp.user_playlist_replace_tracks(user_id,playlist_id,recommendation_ids)
	return



def delete_playlist(token_data,db,table,user_id,playlist_id):
	sp = spotipy.Spotify(auth=token_data['access_token']) 
	sp.user_playlist_unfollow(user_id,playlist_id)
	table.query.filter_by(playlist_id=playlist_id).delete()
	db.session.commit()
	return


class AuthUser(object):

	def __init__(self):
		self.auth = oauth2.SpotifyOAuth(
			client_id=SPOTIFY_CLIENT_ID,
			client_secret=SPOTIFY_CLIENT_SECRET,
			redirect_uri=SPOTIFY_REDIRECT_URI,
			scope=SPOTIFY_SCOPE)


	def get_auth_url(self):
		"""Get URL for user authorization flow
		"""
		return self.auth.get_authorize_url()


	def get_token_data(self,url):
		code = self.auth.parse_response_code(url)
		token_data = self.auth.get_access_token(code)
		return token_data


	def refresh_token(self,token_data):
		token_data = self.auth.refresh_access_token(token_data['refresh_token'])
		return token_data

	
	def is_token_expired(self,token_data):
		"""Check if token is still valid"""
		now = int(time.time())
		return token_data['expires_at'] - now < 60




