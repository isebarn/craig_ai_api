from flask import request, jsonify
import repository
from models import User
from functools import wraps

# decorator that checks if the request header has an authorization header and decodes it and verifies that the user exists and calls the function that is decorated
# with the user object of the user that is logged in
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        token = token.split("Bearer ")[-1]
        user_id = repository.decode_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid'}), 403
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'message': 'User does not exist'}), 403
        return f(user, *args, **kwargs)
    return decorated