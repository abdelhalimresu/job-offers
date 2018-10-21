# Pip imports
from flask import request, jsonify
from flask_restplus import Resource, Namespace
from flask_restplus import marshal, fields, marshal_with, reqparse

# Project imports
from api.db import db
from api.models import Offer, User
from api.schemas import OfferSchema

# Exceptions
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

# Create API Namespace for Offers endpoint
offers = Namespace('Offers', description='Job offers related operations')

# Init serializers
offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)

# Models for Swagger documentation
offer_model = offers.model('Model', {
    'title': fields.String,
    'description': fields.String,
    'skills_list': fields.List(fields.String),
})

# Routes definitions

@offers.route("/")
class OfferList(Resource):

    def get(self, user_id):

        offers = Offer.query.filter_by(user_id=user_id).all()

        if offers:
            result = offers_schema.dump(offers)
            return {"offers": result, "count": len(result)}, 200

        else:
            return {"message": "No offers to show"}, 404

    @offers.expect(offer_model)
    def post(self, user_id):
        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            result = offer_schema.load(json_data)
            offer = Offer(**result, user_id=user_id)
            offer.create()

        except ValidationError as err:
            return err.messages, 400

        except IntegrityError:
            return {"message": "Invalid user id"}, 400

        result = offer_schema.dump(offer.query.get(offer.id))
        return result, 201


@offers.route("/<int:id>")
class OfferItem(Resource):

    def get(self, user_id, id):
        offer = Offer.query.filter_by(id=id, user_id=user_id).first()

        if offer:
            result = offer_schema.dump(offer)
            return result, 200

        else:
            return {"message": "offer not found {}".format(id)}, 404

    @offers.expect(offer_model)
    def put(self, user_id, id):
        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'}, 400

        else:
            offer = Offer.query.filter_by(id=id, user_id=user_id).first()

            if offer:

                try:
                    result = offer_schema.load(json_data, partial=True)
                    offer.update(**result)
                    return offer_schema.dump(offer), 200

                except ValidationError as err:
                    return err.messages, 400                

            else:
                return {"message": "Invalid user id"}, 404

    def delete(self, user_id, id):
        offer = Offer.query.filter_by(id=id, user_id=user_id).first()

        if offer:
            offer.delete()
            return {"message": "offer deleted {}".format(id)}, 200

        else:
            return {"message": "offer not found {}".format(id)}, 404