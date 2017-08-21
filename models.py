from app import db


class UserRefreshToken(db.Model):
	__tablename__ = 'user_refresh_token'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(), unique=True)
	refresh_token = db.Column(db.String(), unique=True)
	stored_on = db.Column(db.String(), unique=False)

	def __init__(self, user_id, refresh_token, stored_on):
		self.user_id = user_id
		self.refresh_token = refresh_token
		self.stored_on = stored_on

	def __repr__(self):
		return '<User Id %r>' % self.user_id


class UserPlaylists(db.Model):
	__tablename__ = 'user_playlists'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(), unique=False)
	playlist_id = db.Column(db.String(), unique=True)
	playlist_name = db.Column(db.String(), unique=False)
	playlist_seed = db.Column(db.String(), unique=False)
	seed_attributes = db.Column(db.String(), unique=False) 
	created_at = db.Column(db.String(), unique=False) 

	def __init__(self,user_id,playlist_id,playlist_name,playlist_seed,seed_attributes,created_at):
		self.user_id = user_id
		self.playlist_id = playlist_id
		self.playlist_name = playlist_name
		self.playlist_seed = playlist_seed
		self.seed_attributes = seed_attributes
		self.created_at = created_at

	def __repr__(self):
		return '<playlist_id %r>' % self.playlist_id