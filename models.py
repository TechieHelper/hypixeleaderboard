from main import db


class Result(db.Model):
	__tablename__ = 'usernames'

	uuid = db.Column(db.String(), primary_key=True)
	username = db.Column(db.String())

	def __init__(self, uuid, username):
		self.uuid = uuid
		self.username = username
