"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException

from flask import Flask, request, jsonify, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from flask_cors import CORS
from api.models import db, User , FavoriteMovie, FavoriteSeries, Comment, PasswordToken
from api.utils import generate_sitemap, APIException

import resend
from datetime import timedelta
import random
import string
import secrets
import os




api = Blueprint('api', __name__)

app = Flask(__name__)

# Allow CORS requests to this API
CORS(api, supports_credentials=True)

app.config["JWT_SECRET_KEY"] = "GoldRoad0503"

users = []
reset_tokens = {}

@api.route('/user', methods=['GET'])
@jwt_required()
def get_user():

    email = get_jwt_identity()
    json = {
        "email" : str(email["email"]),
        "id" : str(email["id"]),
        "name" : str(email["firstName"]),
        "lastName" : str(email["lastName"])
    }
    return jsonify(json)


@api.route('/signup', methods=['POST'])
def signup():
    # Process the information coming from the client
    user_data = request.get_json()
    print(user_data)

    # We create an instance without being recorded in the database
    user = User()
    user.firstName = user_data["firstName"]
    user.lastName = user_data["lastName"]
    user.email = user_data["email"]
    user.password = user_data["password"]
    user.confirmPassword = user_data["confirmPassword"]
    user.is_active = True

    if not (user.firstName and user.lastName and user.email and user.password and user.confirmPassword):
        return jsonify({'message': 'All fields are required'}), 400
    
    # Check if passwords match
    if (user.password != user.confirmPassword):
        return jsonify({'error': 'Password and Confirm Password do not match'}), 400

    # Check if the user with the same email already exists (you should use a database)
    existing_user = next((user for user in users if user['email'] == user.email), None)
    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 400


    # We tell the database we want to record this user and execute the command provided
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@api.route("/login", methods=["POST"])
def create_token():
    user_data = request.get_json()

    email = user_data.get("email", None)
    password = user_data.get("password", None)

    user = User.query.filter_by(email=email).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Bad username or password"), 401

    # Notice that we are passing in the actual sqlalchemy user object here
    access_token = create_access_token(identity=user.serialize())
    return jsonify(access_token=access_token)

    response_body = {
        "message": "The user has been created without a problem"
    }
    return jsonify(response_body), 200




@api.route('/users')
def handle_users():
    users = User.query.all()
    return jsonify([p.serialize() for p in users]), 200

@api.route('/users/<int:user_id>', methods=['PUT', 'GET'])
def handle_user(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)
        return jsonify(user.serialize()), 200
    
    if request.method == 'PUT':
        user = User.query.get(user_id)
        user_data = request.get_json()
        user.password = user_data["password"]
        user.confirmPassword = user_data["password"]
        db.session.commit()
        return jsonify({"msg": "Password changed"}), 200

@api.route('/users/<int:user_id>/edit', methods=['PUT'])
def edit_user(user_id):
    user = User.query.get(user_id)
    user_data = request.get_json()
    user.firstName = user_data["firstName"]
    user.lastName = user_data["lastName"]
    db.session.commit()
    return jsonify({"msg": "User profile data changed"}), 200    
    

@api.route('/users/<int:user_id>/favorites', methods=['GET'])
def handle_userFavorites(user_id):
    userFavorites = []
    favoriteMovie = FavoriteMovie.query.all()
    favoriteSeries = FavoriteSeries.query.all()
    for favoriteM in favoriteMovie:
        if favoriteM.userId == user_id:
            userFavorites.append(favoriteM)
    for favoriteS in favoriteSeries:
        if favoriteS.userId == user_id:
            userFavorites.append(favoriteS)
    return jsonify([userFavorite.serialize() for userFavorite in userFavorites]), 200

    
@api.route('/users/<int:user_id>/favorites/movie/<int:movie_id>', methods=['POST'])
def add_favoriteMovie(user_id, movie_id):
    favorite_data = request.get_json()

    favorite = FavoriteMovie()
    favorite.userId = user_id
    favorite.movieId = movie_id
    favorite.title = favorite_data["title"]
    favorite.status = favorite_data["status"]
    favorite.poster = favorite_data["poster"]
    favorite.runtime = favorite_data["runtime"]
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "favorite Movie was added"}), 200

@api.route('/users/<int:user_id>/favorites/movie/<int:movie_id>', methods=['PUT'])
def manage_favoriteMovie(user_id, movie_id):
    favorite_data = request.get_json()
    favorites = FavoriteMovie.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.movieId == movie_id:
            favorite.status = favorite_data["status"]
            db.session.commit()
            return jsonify({"msg": "favorite Movie was updated"}), 200
    
@api.route('/users/<int:user_id>/favorites/movie/<int:movie_id>', methods=['DELETE'])
def delete_userFavorites(user_id, movie_id):
    favorites = FavoriteMovie.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.movieId == movie_id:
            userFavorite = favorite
            db.session.delete(userFavorite)
            db.session.commit()
            return jsonify({"msg": "favorite Movie was removed"}), 200

@api.route('/users/<int:user_id>/favorites/tv/<int:series_id>', methods=['POST'])
def add_favoriteSeries(user_id, series_id):
    favorite_data = request.get_json()

    favorite = FavoriteSeries()
    favorite.userId = user_id
    favorite.seriesId = series_id
    favorite.title = favorite_data["title"]
    favorite.status = favorite_data["status"]
    favorite.poster = favorite_data["poster"]
    favorite.runtime = favorite_data["runtime"]
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "favorite Series was added"}), 200

@api.route('/users/<int:user_id>/favorites/tv/<int:series_id>', methods=['PUT'])
def manage_favoriteSeries(user_id, series_id):
    favorite_data = request.get_json()
    favorites = FavoriteSeries.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.seriesId == series_id:
            favorite.status = favorite_data["status"]
            db.session.commit()
            return jsonify({"msg": "favorite Series was updated"}), 200

@api.route('/users/<int:user_id>/favorites/tv/<int:series_id>', methods=['DELETE'])
def delete_userSeries(user_id, series_id):
    favorites = FavoriteSeries.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.seriesId == series_id:
            userFavorite = favorite
            db.session.delete(userFavorite)
            db.session.commit()
            return jsonify({"msg": "favorite Series was removed"}), 200



@api.route('/forgot/<user_email>')
def index(user_email):
    resend.api_key = os.environ.get('RESEND_API_KEY')
    user = User.query.filter_by(email=user_email).one_or_none()
    if not user:
        return jsonify("Email Not Found"), 401
    else:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(12))  # Generates a 12-character random password
        user.password = password
        user.confirmPassword = password
        db.session.commit()
        params = {
            "from": "Never Miss <nevermiss@info.mridul.tech>",
            "to": [user.email],
            "subject": "Forgot Password ?",
            "html": "<strong>hello " + user.firstName + " " + user.lastName + "</strong><p>Looks like you've forgotten your password</p>"+"<p>Here is your new Password! : "+ password +"</p>",
        }
        r = resend.Emails.send(params)
        return jsonify(r)
    
@api.route("/forgot_password/<user_email>", methods=["GET"])
def forgot_password(user_email):
    resend.api_key = os.environ.get('RESEND_API_KEY')
    user = User.query.filter_by(email=user_email).one_or_none()
    if user:
        # Generate a random reset token
        reset_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # Store the reset token with the user email
        # reset_tokens[user_email] = reset_token

        passwordToken = PasswordToken()
        passwordToken.userEmail = user_email
        passwordToken.token = reset_token
        db.session.add(passwordToken)
        db.session.commit()

        params = {
        "from": "Never Miss <nevermiss@info.mridul.tech>",
        "to": [user.email],
        "subject": "Forgot Password ?",
        "html": "<strong>hello " + user.firstName + " " + user.lastName + "</strong><p>Looks like you've forgotten your password</p>"+"<p>Here is your reset Link! : "+ os.environ.get('FRONTEND_URL') +"/forgot/"+ reset_token +"</p>",
        }
        resend.Emails.send(params)

        return jsonify({"message": "Password reset link sent to your email"})
    else:
        return jsonify("Email Not Found"), 404


@api.route("/reset_password/<token>", methods=["POST"])
def reset_password(token):
    user_data = request.get_json()
    # Check if the token is valid
    email = verify_reset_token(token)
    
    if email:
        user = User.query.filter_by(email=email.userEmail).one_or_none()
        user.password = user_data["password"]
        user.confirmPassword = user_data["password"]
        db.session.commit()
        return jsonify({"message": "Password reset successful"})
    else:
        return jsonify({"error": "Invalid token"}), 400

def verify_reset_token(token):
    # Check if the token exists in the stored reset_tokens dictionary
    email = PasswordToken.query.filter_by(token=token).one_or_none()

    # If the token exists, remove it from the dictionary (one-time use)
    if email:
        db.session.delete(email)
        db.session.commit()

    return email



@api.route('/comments', methods=['GET'])
def handle_getCommets():
    userComments = []
    comments = Comment.query.all()
    for comment in comments:
        userComments.append(comment)
    return jsonify([userComment.serialize() for userComment in userComments]), 200

@api.route('/user/<int:user_id>/comments', methods=['GET'])
def handle_userComments(user_id):
    userComments = []
    comments = Comment.query.all()
    for comment in comments:
        if comment.userId == user_id:
            userComments.append(comment)
    return jsonify([userComment.serialize() for userComment in userComments]), 200


@api.route('/users/<int:user_id>/comment/<target_type>/<int:target_id>', methods=['POST'])
def add_Comment(user_id, target_id, target_type):
    comment_data = request.get_json()

    comment = Comment()
    comment.userId = user_id
    comment.targetId = target_id
    comment.targetType = target_type
    comment.userName = comment_data["userName"]
    comment.text = comment_data["text"]
    comment.targetName = comment_data["targetName"]
    comment.targetPoster = comment_data["targetPoster"]
    db.session.add(comment)
    db.session.commit()
    return jsonify({"msg": "Comment was added"}), 200
    
@api.route('/users/<int:user_id>/comment/<target_type>/<int:target_id>', methods=['DELETE'])
def delete_Comment(user_id, target_id, target_type):
    comments = Comment.query.all()
    for comment in comments:
        if comment.userId == user_id and comment.targetId == target_id and comment.targetType == target_type:
            userComment = comment
            db.session.delete(userComment)
            db.session.commit()
            return jsonify({"msg": "Comment was removed"}), 200
