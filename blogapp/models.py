from datetime import datetime
from blogapp import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from blogapp import login
from hashlib import md5

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.now)

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	# To get the image of specified size from Gravatar Service
	def avatar(self, size):
		hash_val = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(hash_val, size)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

# Flask-login uses this function to load the current user since it
# knows nothing about databases and only knows the id of the logged in user
@login.user_loader
def load_user(id):
	return User.query.get(int(id))
