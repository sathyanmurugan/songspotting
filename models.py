from app import db


class UserRefreshToken(db.Model):
	__tablename__ = 'user_refresh_token'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(80), unique=True)
	refresh_token = db.Column(db.String(500), unique=True)

	def __init__(self, user_id, refresh_token):
		self.user_id = user_id
		self.refresh_token = refresh_token

	def __repr__(self):
		return '<User Id %r>' % self.user_id
