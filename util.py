import os
import spotipy.oauth2 as oauth2
import time

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = os.environ['SPOTIFY_REDIRECT_URI']
SPOTIFY_SCOPE = """
playlist-modify-public
playlist-modify-private
user-read-email
user-top-read playlist-read-private
"""

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
		self._store_token(token_data) #store token in DB
		return token_data

	def _store_token(self,token_data):

		#if user already in db, overwrite, else new row
		return

	def refresh_token(self,token_data):
		token_data = self.auth.refresh_access_token(token_data['refresh_token'])
		self._store_token(token_data) #store token in DB
		return token_data

	
	def is_token_expired(self,token_data):
		"""Check if token is still valid"""
		now = int(time.time())
		return token_data['expires_at'] - now < 60
