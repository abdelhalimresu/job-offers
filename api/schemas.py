from marshmallow import fields, Schema

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class OfferSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    skills_list = fields.List(fields.String, required=True)
    creation_date = fields.DateTime(dump_only=True)
    modification_date = fields.DateTime(dump_only=True)
