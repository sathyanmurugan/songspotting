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
	now = datetime.datetime.now()

	if user is None:
		#Add refresh_token
		row = table(user_id,token_data['refresh_token'],now)
		db.session.add(row)
	else:
		#update refresh_token
		user.refresh_token = token_data['refresh_token']
		user.stored_date = now
	db.session.commit()
	return


def create_playlist(access_token,db,table,**kwargs):
	sp = spotipy.Spotify(auth=access_token) 
	response = sp.user_playlist_create(kwargs['user_id'],kwargs['playlist_name'])
	playlist_id = response['id']
	now = datetime.datetime.now()

	#Add playlist details to database
	row = table(kwargs['user_id'],playlist_id,kwargs['playlist_name'],kwargs['playlist_seed'],kwargs['seed_attributes'],now)
	db.session.add(row)
	db.session.commit()
	return playlist_id


def reload_playlist(access_token,table,user_id,playlist_id):
	sp = spotipy.Spotify(auth=access_token)

	playlist = table.query.filter_by(playlist_id=playlist_id).first()
	if playlist is None:
		return

	recommendation_ids = None
	
	if playlist.playlist_seed == 'favorite_tracks':
		results = sp.current_user_top_tracks(limit=20, time_range=playlist.seed_attributes)
		result_ids = [result['id'] for result in results['items']]
		shuffle(result_ids)
		if len(result_ids) > 0:
			recommendations = sp.recommendations(seed_tracks=result_ids[0:5],limit=50)
			recommendation_ids = [track['id'] for track in recommendations['tracks']]

	elif playlist.playlist_seed == 'favorite_artists':
		results = sp.current_user_top_artists(limit=20, time_range=playlist.seed_attributes)
		result_ids = [result['id'] for result in results['items']]
		shuffle(result_ids)
		if len(result_ids) > 0:
			recommendations = sp.recommendations(seed_artists=result_ids[0:5],limit=50)
			recommendation_ids = [track['id'] for track in recommendations['tracks']]

	elif playlist.playlist_seed == 'genre':
		recommendations = sp.recommendations(seed_genres=[playlist.seed_attributes],limit=50)
		recommendation_ids = [track['id'] for track in recommendations['tracks']]		

	elif playlist.playlist_seed == 'playlist':
		tracks = get_tracks_in_playlist(access_token,user_id,playlist.seed_attributes)
		shuffle(tracks)
		if len(tracks) > 0:
			recommendations = sp.recommendations(seed_tracks=tracks[0:5],limit=50)
			recommendation_ids = [track['id'] for track in recommendations['tracks']]			

	if recommendation_ids:
		sp.user_playlist_replace_tracks(user_id,playlist_id,recommendation_ids)
	return



def delete_playlist(access_token,db,table,user_id,playlist_id):
	sp = spotipy.Spotify(auth=access_token) 
	sp.user_playlist_unfollow(user_id,playlist_id)
	table.query.filter_by(playlist_id=playlist_id).delete()
	db.session.commit()
	return


def get_user_playlist_ids(access_token,limit=50,offset=0):
	sp = spotipy.Spotify(auth=access_token) 
	playlists = sp.current_user_playlists(limit=limit,offset=offset)
	playlist_ids = [pl['id'] for pl in playlists['items']]

	#Max returned ids per call is 50.
	#The offset serves as an index, so if the total is higher than 
	#the limit, we can offset the index and query the remaining records
	while len(playlist_ids) < playlists['total']:
		offset+=limit
		playlists = sp.current_user_playlists(limit=limit,offset=offset)
		playlist_ids.extend([pl['id'] for pl in playlists['items']])

	return playlist_ids


def get_user_playlists(access_token,limit=50,offset=0):
	sp = spotipy.Spotify(auth=access_token) 
	playlists = sp.current_user_playlists(limit=limit,offset=offset)
	user_playlists = [(pl['id'],pl['name']) for pl in playlists['items']]

	#Max returned ids per call is 50.
	#The offset serves as an index, so if the total is higher than 
	#the limit, we can offset the index and query the remaining records
	while len(user_playlists) < playlists['total']:
		offset+=limit
		playlists = sp.current_user_playlists(limit=limit,offset=offset)
		user_playlists.extend([(pl['id'],pl['name']) for pl in playlists['items']])

	return user_playlists

def get_tracks_in_playlist(access_token,user_id,playlist_id,limit=50,offset=0):
	sp = spotipy.Spotify(auth=access_token) 
	result = sp.user_playlist_tracks(user_id,playlist_id,limit=limit,offset=offset)
	tracks = [t['track']['id'] for t in result['items']]
	print(result)
	#Max returned ids per call is 50.
	#The offset serves as an index, so if the total is higher than 
	#the limit, we can offset the index and query the remaining records
	while len(tracks) < result['total']:
		offset+=limit
		result = sp.user_playlist_tracks(user_id,playlist_id,limit=limit,offset=offset)
		tracks.extend([t['track']['id'] for t in result['items']])	
	return tracks

def get_user_data(access_token):
	sp = spotipy.Spotify(auth=access_token)
	response = sp.current_user()
	user_data = {k:v for k,v in response.items() if k in ['id','display_name','email','followers']}
	user_data['followers'] = user_data['followers']['total']
	user_data['user_id'] = user_data.pop('id')
	return user_data


def store_user_data(user_data,db,table):
	
	#Check if user exists in dB
	user = table.query.filter_by(user_id=user_data['user_id']).first()
	now = datetime.datetime.now()

	if user is None:
		row = table(user_data['user_id'],user_data['display_name'],
			user_data['email'],user_data['followers'],now,now)
		db.session.add(row)
	else:
		#update user
		user.display_name = user_data['display_name']
		user.email = user_data['email']
		user.followers = user_data['followers']
		user.updated_at = now

	db.session.commit()
	return


def store_comment(db,table,email,comment):
	now = datetime.datetime.now()
	row = table(email,comment,now)
	db.session.add(row)
	db.session.commit()
	return


def get_genres(access_token):
	sp = spotipy.Spotify(auth=access_token)
	genres = sp.recommendation_genre_seeds()['genres']
	return genres

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


	def refresh_token(self,refresh_token):
		token_data = self.auth.refresh_access_token(refresh_token)
		return token_data

	
	def is_token_expired(self,token_data):
		"""Check if token is still valid"""
		now = int(time.time())
		return token_data['expires_at'] - now < 60




