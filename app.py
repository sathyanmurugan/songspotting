import flask
import util
import os
import spotipy.oauth2 as oauth2

app = flask.Flask(__name__)
app.debug = os.environ['DEBUG']
app.secret_key = os.environ['APP_SECRET']

#Initilize Auth Class
auth = util.AuthUser()

@app.route('/')
def main():
	if 'token_data' in flask.session:
		try:
			#Check if token is expired, and if so, refresh
			if auth.is_token_expired(flask.session['token_data']):
				token_data = auth.refresh_token(flask.session['token_data'])
				flask.session['token_data'] = token_data
			else:
				pass
			return flask.redirect(flask.url_for('factory'))

		except:
			#in case user removed permissions for the app, the old tokens are no longer valid
			#we need to reauthenticate
			return flask.render_template('main.html')

	else:
		return flask.render_template('main.html')

@app.route('/login')
def login():
	#Redirect user to Spotify for authentication	
	return flask.redirect(auth.get_auth_url())


@app.route('/usercheck')
def usercheck():
	"""authenticated user arrives here
	"""
	token_data = auth.get_token_data(flask.request.url)
	flask.session['token_data'] = token_data
	return flask.redirect(flask.url_for('factory'))

@app.route('/factory')
def factory():
	return str(flask.session['token_data'])


if __name__ == '__main__':
    app.run()