import flask
import util
import os
import spotipy.oauth2 as oauth2
from flask_sqlalchemy import SQLAlchemy

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
			else:
				pass
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
	token_data = auth.get_token_data(flask.request.url) 
	util.store_refresh_token(token_data,db=db,table=UserRefreshToken)
	flask.session['token_data'] = token_data
	return flask.redirect(flask.url_for('factory'))

@app.route('/factory')
def factory():
	"""User's factory page
	"""
	#If no session data available, send user back to main page
	if 'token_data' not in flask.session:
		return flask.redirect(flask.url_for('main'))
	
	else:
		#Try to authenticate user
		try:
			#Check if token is expired, and if so, refresh
			if auth.is_token_expired(flask.session['token_data']):
				token_data = auth.refresh_token(flask.session['token_data'])
				flask.session['token_data'] = token_data
			else:
				pass

			return str(flask.session['token_data'])

		except:
			#in case user removed permissions for the app, or if we chanegd the scopes,
			#the old tokens are no longer valid, we need to reauthenticate
			return flask.redirect(flask.url_for('main'))	

	


@app.route('/test')
def test():
	return str(auth._store_token(flask.session['token_data']))
if __name__ == '__main__':
    app.run()