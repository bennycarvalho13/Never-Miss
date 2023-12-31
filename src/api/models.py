from flask_sqlalchemy import SQLAlchemy
from hmac import compare_digest


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    confirmPassword = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'User {self.firstName} {self.lastName}'

    def check_password(self, password):
        return compare_digest(password, self.password)

    def serialize(self):
        return {
            "id": self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email
            # do not serialize the password, its a security breach
        }

    
class FavoriteMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    movieId = db.Column(db.Integer,  nullable=False)
    title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    poster = db.Column(db.String(120), nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    user = db.relationship(User)
    def __repr__(self):
        return '<FavoriteMovie %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "movieId": self.movieId,
            "title": self.title,
            "status": self.status,
            "poster": self.poster,
            "runtime": self.runtime
        }

class FavoriteSeries(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    seriesId = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    poster = db.Column(db.String(80), nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    user = db.relationship(User)
    def __repr__(self):
        return '<FavoriteSeries %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "seriesId": self.seriesId,
            "title": self.title,
            "status": self.status,
            "poster": self.poster,
            "runtime": self.runtime
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    userName = db.Column(db.String(120), nullable=False)
    targetId = db.Column(db.Integer,  nullable=False)
    targetType = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(250), nullable=False)
    targetName = db.Column(db.String(80), nullable=True)
    targetPoster = db.Column(db.String(250), nullable=True)
    user = db.relationship(User)
    def __repr__(self):
        return '<Comment %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "userName": self.userName,
            "target_type": self.targetType,
            "target_id": self.targetId,
            "targetName": self.targetName,
            "targetPoster": self.targetPoster,
            "text": self.text
        }

class PasswordToken(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    userEmail = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(120), nullable=False)
    def __repr__(self):
        return '<FavoriteMovie %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "userEmail": self.userEmail,
            "token": self.token,
        }