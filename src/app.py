"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager
from api.utils import APIException, generate_sitemap
from api.models import db, User , FavoriteMovie, FavoriteSeries
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

#from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

jwt = JWTManager(app)

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)



# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)


@app.route('/users')
def handle_users():
    users = User.query.all()
    return jsonify([p.serialize() for p in users]), 200

@app.route('/signup', methods=['POST'])
def sign_up():
    user_data = request.get_json()
    
    # We create an instance without being recorded in the database
    user = User()
    user.email = user_data["email"]
    user.password = user_data["password"]
    user.is_active = True

    # We tell the database we want to record this user
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "The user has been created successfully"}), 200


@app.route("/login", methods=["POST"])
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


@app.route("/hello", methods=["GET"])
def get_hello():
    
    email = get_jwt_identity()
    dictionary = {
        "message": "welcome " + email
    }
    return jsonify(dictionary)

@app.route('/users/<int:user_id>', methods=['PUT', 'GET'])
def handle_user(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)
        return jsonify(user.serialize()), 200
    
    if request.method == 'PUT':
        user = User.query.get(user_id)
        body = request.get_json()
        user.email = body.email
        db.session.commit()
        return jsonify(user.serialize()), 200
    
    

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
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

    
@app.route('/users/<int:user_id>/favorites/movie/<int:movie_id>', methods=['POST'])
def add_favoriteMovie(user_id, movie_id):
    favorite = FavoriteMovie(userId = user_id, movieId = movie_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "favorite Movie was added"}), 200
    
@app.route('/users/<int:user_id>/favorites/movie/<int:movie_id>', methods=['DELETE'])
def delete_userFavorites(user_id, movie_id):
    favorites = FavoriteMovie.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.movieId == movie_id:
            userFavorite = favorite
            db.session.delete(userFavorite)
            db.session.commit()
            return jsonify({"msg": "favorite Movie was removed"}), 200

@app.route('/users/<int:user_id>/favorites/series/<int:series_id>', methods=['POST'])
def add_favoriteSeries(user_id, series_id):
    favorite = FavoriteSeries(userId = user_id, seriesId = series_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "favorite Series was added"}), 200

@app.route('/users/<int:user_id>/favorites/series/<int:series_id>', methods=['DELETE'])
def delete_userSeries(user_id, series_id):
    favorites = FavoriteSeries.query.all()
    for favorite in favorites:
        if favorite.userId == user_id and favorite.seriesId == series_id:
            userFavorite = favorite
            db.session.delete(userFavorite)
            db.session.commit()
            return jsonify({"msg": "favorite Series was removed"}), 200
