# Built-in
from functools import wraps

# Pip imports
from flask import _request_ctx_stack, current_app, request, jsonify
import jwt

# Project imports
from api.models import User


auth = {
    'JWT Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}


class AuthError(Exception):
    """The Authorization exception"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def handle_auth_exception(ex):
    """The Authorization exception handler"""
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"message": "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "jwt":
        raise AuthError({"message": "Authorization header must 'JWT token'"}, 401)

    elif len(parts) == 1:
        raise AuthError({"message": "Token not found"}, 401)

    elif len(parts) > 2:
        raise AuthError({"message": "Authorization header must 'JWT token'"}, 401)

    token = parts[1]
    return token


def require_auth(f):
    """Wraps Resources endpoints to decode the Token and assing the current user of the request"""
    @wraps(f)
    def wrapped(*args, **kwargs):

        try:
            token = get_token_auth_header()

            # Decode token
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=['HS256'])

            user = User.query.filter_by(id=payload["id"]).first()
            # Assign the user to the request's curent user field
            _request_ctx_stack.top.request.current_user = user

        except AuthError as ex:
            return handle_auth_exception(ex)

        # Some parsing exceptions raised by jwt package
        except Exception:
            response = jsonify({"message": "Invalid Token"})
            response.status_code = 401
            return response

        return f(*args, **kwargs)
    return wrapped