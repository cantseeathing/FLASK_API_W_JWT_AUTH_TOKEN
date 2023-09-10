import uuid
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("items", __name__, description="Operations on items")


@blp.route('/items/<string:item_id>')
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item, 200

    @blp.arguments(ItemUpdateSchema)
    @blp.response(201, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data['price']
            item.name = item_data['name']
        else:
            item = ItemModel(id=item_id, **item_data)
        db.session.add(item)
        db.session.commit()

        return item
        # raise NotImplementedError("Updating an Item is not implemented!")

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}, 200


@blp.route('/items')
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        # if item_data["store_id"] not in stores:
        #     abort(404, message="Store not found!")
        #     # return {"message": "Store not found!"}, 404
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred when inserting the item to the DB!")
        return item, 201
