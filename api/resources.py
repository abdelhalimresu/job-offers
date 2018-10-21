from flask import request, jsonify
from flask_restplus import Resource, Namespace
from flask_restplus import marshal, fields, marshal_with, reqparse
from api.db import db
from api.models import Offer, User
from api.schemas import OfferSchema

# Create API Namespace for Offers endpoint
offers = Namespace('Offers', description='Job offers related operations')

# Init serializers
offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)


# Routes definitions

@offers.route("/")
class OfferList(Resource):

    def get(self, user_id):

        offers = Offer.query.filter_by(user_id=user_id).all()
        if offers:
            result = offers_schema.dump(offers)
            return {"offers": result.data, "count": len(result.data)}, 200
        else:
            return {"message": "No offer to show"}, 404


@offers.route("/<int:id>")
class OfferItem(Resource):

    def get(self, user_id, id):
        offer = Offer.query.filter_by(id=id, user_id=user_id).first()
        if offer:
            result = offer_schema.dump(offer)
            return result.data, 200
        else:
            return {"message": "offer not found {}".format(id)}, 404
