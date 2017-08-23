from app import db


class Users(db.Model):
	__tablename__ = 'users'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(), unique=False)
	display_name = db.Column(db.String(), unique=True)
	email = db.Column(db.String(), unique=False)
	followers = db.Column(db.String(), unique=False)
	created_at = db.Column(db.DateTime, unique=False)
	updated_at = db.Column(db.DateTime, unique=False)

	def __init__(self,user_id,display_name,email,followers,created_at,updated_at):
		self.user_id = user_id
		self.display_name = display_name
		self.email = email
		self.followers = followers
		self.created_at = created_at
		self.updated_at = updated_at

	def __repr__(self):
		return '<user_id %r>' % self.user_id


class UserRefreshToken(db.Model):
	__tablename__ = 'user_refresh_token'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(), unique=True)
	refresh_token = db.Column(db.String(), unique=True)
	stored_date = db.Column(db.DateTime, unique=False)

	def __init__(self, user_id, refresh_token, stored_date):
		self.user_id = user_id
		self.refresh_token = refresh_token
		self.stored_date = stored_date

	def __repr__(self):
		return '<Refresh Token %r>' % self.refresh_token


class UserPlaylists(db.Model):
	__tablename__ = 'user_playlists'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(), unique=False)
	playlist_id = db.Column(db.String(), unique=True)
	playlist_name = db.Column(db.String(), unique=False)
	playlist_seed = db.Column(db.String(), unique=False)
	seed_attributes = db.Column(db.String(), unique=False) 
	created_date = db.Column(db.DateTime, unique=False) 

	def __init__(self,user_id,playlist_id,playlist_name,playlist_seed,seed_attributes,created_date):
		self.user_id = user_id
		self.playlist_id = playlist_id
		self.playlist_name = playlist_name
		self.playlist_seed = playlist_seed
		self.seed_attributes = seed_attributes
		self.created_date = created_date

	def __repr__(self):
		return '<playlist_id %r>' % self.playlist_id