# pip install python-dotenv
# pip install flask
# pip freeze > requirements.txt
# pip install -r requirements.txt
# $env:FLASK_APP = "main"

# BUILDING DOCKER IMAGE
# docker build -t flask_api_ex .

# RUNNING DOCKER
# docker run -p 5000:5000 flask_api_ex

# RUNNING DOCKER IN THE BACKGROUND
# docker run -dp 5000:5000 flask_api_ex

# DOCKER CONTAINER
# docker run -dp 5000:5000 -w /app -v "/c/Users/mahmo/PycharmProjects/flask_smorest_api_ex:/app" flask_api_ex

# TO RUN THE FLASK APP IN CONSOLE
# flask run

import uuid
from flask import Flask, request, redirect, cli, jsonify
from flask_smorest import abort, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import sqlalchemy
from db import db
import models
import os
import secrets
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.docs import blp as DocsBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from dotenv import load_dotenv
from blocklist import BLOCKLIST

load_dotenv()


# print(secrets.SystemRandom().getrandbits(128))

def create_app(db_url=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    db.init_app(app)

    api = Api(app)

    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(DocsBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

# @app.get('/stores')
# def get_stores():
#     return {"stores": list(stores.values())}


# @app.get('/items')
# def get_items():
#     return {"items": list(items.values())}


# @app.post("/stores")
# def create_store():
#     store_data = request.get_json()
#     store_id = uuid.uuid4().hex
#     store = {**store_data, "id": store_id}
#     stores[store_id] = store
#     return store, 201


# @app.post('/item')
# def create_item():
#     item_data = request.get_json()
#     if item_data["store_id"] not in stores:
#         abort(404, message="Store not found!")
#         # return {"message": "Store not found!"}, 404
#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id": item_id}
#     items[item_id] = item
#     return item, 201


# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     if stores.get(store_id) is not None:
#         return stores[store_id]
#     abort(404, message="Store not found!")
#     # return {"message": "Store not found!"}, 404


# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     if items.get(item_id) is not None:
#         return items[item_id]
#     abort(404, message="Item not found!")
#     # return {"message": "Item not found!"}, 404


# @app.delete('/item/<string:item_id>')
# def delete_item(item_id):
#     if items.get(item_id) is not None:
#         del items[item_id]
#         return {"message": "Item Deleted!"}
#     abort(404, message="Item not found!")


# @app.delete('/store/<string:store_id>')
# def delete_store(store_id):
#     if stores.get(store_id) is not None:
#         del stores[store_id]
#         return {"message": "Store Deleted!"}
#     abort(404, message="Store not found!")


# @app.put('/item/<string:item_id>')
# def update_item(item_id):
#     item_data = request.get_json()
#     if items.get(item_id) is not None:
#         item = items[item_id]
#         item |= item_data
#         return {"message": "Item Updated!"}
#     abort(404, message="Item not found!")


# @app.get('/')
# def main():
#     return redirect("/swagger-ui", code=302)
