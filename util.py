import os
import spotipy.oauth2 as oauth2
import time
import spotipy


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


def store_refresh_token(token_data,db,table):

	#Get user_id
	sp = spotipy.Spotify(auth=token_data['access_token']) 
	user_id = sp.current_user()['id']

	#Check if user exists in dB
	user = table.query.filter_by(user_id=user_id).first()

	if user is None:
		#Add user and refresh_token
		row = table(user_id,token_data['refresh_token'])
		db.session.add(row)
	else:
		#update refresh_token
		user.refresh_token = token_data['refresh_token']

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




