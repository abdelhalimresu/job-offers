# Pip imports
from flask import request
from flask_restplus import Resource, Namespace
from flask_restplus import marshal, fields, marshal_with, reqparse

# Project imports
from api.db import db
from api.models import Offer, User
from api.schemas import OfferSchema, UserSchema
from api.auth import require_auth

# Exceptions
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


# Create API Namespace for Offers endpoint
offers = Namespace('Offers', description='Job offers related operations')
users = Namespace('Users', description='Users related operations')


# Init serializers
user_schema = UserSchema()
offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)


# Models for Swagger documentation
offer_model = offers.model('OfferModel', {
    'title': fields.String,
    'description': fields.String,
    'skills_list': fields.List(fields.String)
})

user_model = users.model('UserModel', {
    'username': fields.String,
    'password': fields.String
})


# Routes definitions

@offers.route("/")
class OfferList(Resource):

    @require_auth
    @offers.doc(security='JWT Token')
    def get(self, user_id):
        """Get job offers for a specific user"""

        offers = Offer.query.filter_by(user_id=user_id).all()

        if offers:
            result = offers_schema.dump(offers)
            return {"offers": result, "count": len(result)}, 200

        else:
            return {"message": "No offers to show"}, 404

    @require_auth
    @offers.doc(security='JWT Token')
    @offers.expect(offer_model)
    def post(self, user_id):
        """Create a job offer"""

        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Only owner can create offers
        if request.current_user.id != user_id:
            return {'message': 'Unauthorized'}, 401

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

    @require_auth
    @offers.doc(security='JWT Token')
    def get(self, user_id, id):
        """Get a job offer by id"""

        offer = Offer.query.filter_by(id=id, user_id=user_id).first()

        if offer:
            result = offer_schema.dump(offer)
            return result, 200

        else:
            return {"message": "offer not found {}".format(id)}, 404

    @require_auth
    @offers.doc(security='JWT Token')
    @offers.expect(offer_model)
    def put(self, user_id, id):
        """Edit a job offer"""

        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Only owner can edit offers
        if request.current_user.id != user_id:
            return {'message': 'Unauthorized'}, 401

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

    @require_auth
    @offers.doc(security='JWT Token')
    def delete(self, user_id, id):
        """Delete a job offer"""

        offer = Offer.query.filter_by(id=id, user_id=user_id).first()

        # Only owner can delete offers
        if request.current_user.id != user_id:
            return {'message': 'Unauthorized'}, 401

        if offer:
            offer.delete()
            return {"message": "offer deleted {}".format(id)}, 200

        else:
            return {"message": "offer not found {}".format(id)}, 404


@users.route("/register")
class UserRegister(Resource):

    @offers.expect(user_model)
    def post(self):
        """Register a new user"""

        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            result = user_schema.load(json_data)
            password = result.pop("password", None)
            user = User(**result)
            user.create(password)

        except ValidationError as err:
            return err.messages, 400

        return {"username": user.username, "id": user.id}, 201


@users.route("/login")
class UserLogin(Resource):

    @offers.expect(user_model)
    def post(self):
        """Authenticate and retrieve an api token"""

        json_data = request.get_json()

        if not json_data:
            return {'message': 'No username/password provided'}, 400

        try:
            result = user_schema.load(json_data)
            user = User.query.filter_by(username=result["username"]).first()
            if user and user.check_password(result["password"]):
                return {"id": user.id, "token": user.generate_token()}, 200

        except ValidationError as err:
            return err.messages, 400
        
        return {'message': 'Invalid username/password'}, 400