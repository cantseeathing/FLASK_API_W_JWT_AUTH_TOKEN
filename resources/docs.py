from flask import redirect
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("docs", __name__, description="API Documentation")


@blp.route('/')
class ItemList(MethodView):
    @blp.response(200)
    def get(self):
        return redirect("/swagger-ui", code=302)
