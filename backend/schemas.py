from marshmallow import Schema, fields, validate

class SignupSchema(Schema):
    username = fields.Str(required=True,validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True,load_only=True,validate=validate.Length(min=6))
    password_confirmation = fields.Str(required=True,load_only=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True,load_only=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()

class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True,validate=validate.Range(min=1, max=1440))
    notes = fields.Str(allow_none=True,validate=validate.Length(max=500))
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)