from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    password = fields.Str()


class OfferSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    skills_list = fields.List(fields.String)
    creation_date = fields.DateTime(dump_only=True)
    modification_date = fields.DateTime(dump_only=True)
