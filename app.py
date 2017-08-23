import flask
import util
import os
import spotipy.oauth2 as oauth2
from flask_sqlalchemy import SQLAlchemy
import json

app = flask.Flask(__name__)
app.debug = os.environ['DEBUG']
app.secret_key = os.environ['APP_SECRET']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import * # Needs to be after app is created

#Initilize Auth Class
auth = util.AuthUser()

@app.route('/')
def main():

	#If no session data available, show user the main page
	if 'token_data' not in flask.session:
		return flask.render_template('main.html')

	else:
		#Try to send user to factory
		try:
			#Check if token is expired, and if so, refresh
			if auth.is_token_expired(flask.session['token_data']):
				token_data = auth.refresh_token(flask.session['token_data'])
				flask.session['token_data'] = token_data

			return flask.redirect(flask.url_for('factory'))

		except:
			#in case user removed permissions for the app, or if we chanegd the scopes,
			#the old tokens are no longer valid, we need to reauthenticate
			return flask.render_template('main.html')
		

@app.route('/login')
def login():
	#Redirect user to Spotify for authentication	
	return flask.redirect(auth.get_auth_url())


@app.route('/usercheck')
def usercheck():
	"""authenticated user is redirected here from spotify
	"""

	#Store token data and add to session
	token_data = auth.get_token_data(flask.request.url) 
	util.store_refresh_token(token_data,db=db,table=UserRefreshToken)
	flask.session['token_data'] = token_data

	#Get and store user info
	user_data = util.get_user_data(token_data['access_token'])
	flask.session['user_id'] = user_data['user_id']
	util.store_user_data(user_data,db,Users)

	return flask.redirect(flask.url_for('factory'))

@app.route('/factory', methods=['GET','POST'])
def factory():
	"""User's factory page
	"""
	#If no session data available, send user back to main page
	if 'token_data' not in flask.session:
		flask.session.clear()
		return flask.redirect(flask.url_for('main'))
	
	else:
		#Try to authenticate user
		try:
			#Check if token is expired, and if so, refresh the access_token
			if auth.is_token_expired(flask.session['token_data']):
				token_data = auth.refresh_token(flask.session['token_data']['refresh_token'])
				flask.session['token_data'] = token_data

			playlists = UserPlaylists.query.filter_by(user_id=flask.session['user_id']).all()
			return flask.render_template('factory.html',playlists=playlists)

		except Exception as e:
			print(e)
			#in case user removed permissions for the app, or if we chanegd the scopes,
			#the old tokens are no longer valid, we need to reauthenticate
			flask.session.clear()
			return flask.redirect(flask.url_for('main'))	



@app.route('/createPlaylist', methods=['POST'])
def createPlaylist():
    playlistName =  flask.request.form['playlist_name']
    seedType = flask.request.form['seed_type']
    timeFrame = flask.request.form['time_frame']

    token_data = auth.refresh_token(flask.session['token_data']['refresh_token'])
    flask.session['token_data'] = token_data

    playlist_id = util.create_playlist(token_data['access_token'],
    	db=db,table=UserPlaylists,
    	user_id=flask.session['user_id'],
    	playlist_name=playlistName,
    	playlist_seed=seedType,
    	seed_attributes=timeFrame,
    	)
    util.reload_playlist(token_data['access_token'],
    	table=UserPlaylists,user_id=flask.session['user_id'],
    	playlist_id=playlist_id)

    return flask.json.dumps({'status':'success'})

@app.route('/deletePlaylist', methods=['POST'])
def deletePlaylist():
	playlist_id = flask.request.json['playlistId']
	token_data = auth.refresh_token(flask.session['token_data']['refresh_token'])
	flask.session['token_data'] = token_data

	util.delete_playlist(token_data['access_token'],
    	db=db,table=UserPlaylists,
    	user_id=flask.session['user_id'],
    	playlist_id=playlist_id
    	)

	return flask.json.dumps({'status':'success'})

@app.route('/test')
def test():
	return flask.render_template('main.html')
if __name__ == '__main__':
    app.run()