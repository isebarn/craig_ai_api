import secrets
from urllib.parse import urlencode
from app import app
import repository
from flask import redirect, request, jsonify, render_template, session, url_for
from decorators import token_required

# endpoint to sign up with email and password
@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if repository.sign_up(email, password):
        return jsonify({'message': 'success'})
    return jsonify({'message': 'failed'})

# endpoint to login with email and password
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    token = repository.login(email, password)
    if token:
        return jsonify({'token': token})
    return jsonify({'message': 'failed'})

# endpoint to get user information
@app.route('/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify(current_user)

# endpoint to subscribe to basic plan. The endpoint is passed card and billing details
@app.route('/subscribe/basic', methods=['POST'])
@token_required
def subscribe_basic(current_user):
    data = request.get_json()
    card = data['card']
    billing_details = data['billing_details']
    if repository.subscribe_basic(current_user, card, billing_details):
        return jsonify({'message': 'success'})
    return jsonify({'message': 'failed'})

# endpoint to subscribe to pro plan. The endpoint is passed card and billing details
@app.route('/subscribe/pro', methods=['POST'])
@token_required
def subscribe_pro(current_user):
    data = request.get_json()
    card = data['card']
    billing_details = data['billing_details']
    if repository.subscribe_pro(current_user, card, billing_details):
        return jsonify({'message': 'success'})
    return jsonify({'message': 'failed'})

# endpoint to cancel the user's subscription
@app.route('/cancel_subscription', methods=['POST'])
@token_required
def cancel_subscription(current_user):
    if repository.cancel_subscription(current_user):
        return jsonify({'message': 'success'})
    return jsonify({'message': 'failed'})

# handle payment success and failure
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    repository.process_webhook(payload, sig_header)

    return jsonify(success=True)

# endpoint to prompt the openai using repository.get_open_ai_completion
@app.route('/prompt', methods=['POST'])
@token_required
def prompt(current_user):
    data = request.get_json()
    prompt_text = data['prompt_text']
    response = repository.get_open_ai_completion(current_user, prompt_text)
    return jsonify({'response': response})


# endpoint to get all users prompts from repository.get_user_prompts
@app.route('/prompts', methods=['GET'])
@token_required
def get_prompts(current_user):
    prompts = repository.get_user_prompts(current_user)
    return jsonify({'prompts': prompts})

# endpoint to call repository.google_login_method
@app.route('/google_login', methods=['POST'])
def google_login():
    state = secrets.token_urlsafe(16)
    session['state'] = state
    params = {
        'response_type': 'code',
        'client_id': app.config.get('GOOGLE_CLIENT_ID'),
        'redirect_uri': url_for('google_callback', _external=True),
        'scope': 'openid email profile',
        'state': state
    }
    # Redirect the user to the authorization page.
    authorization_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)
    return redirect(authorization_url)

# endpoint to call repository.google_callback_method
@app.route('/google_callback', methods=['GET'])
def google_callback():
    token = repository.google_callback()
    if token:
        return jsonify({'token': token})
    return jsonify({'message': 'failed'})

# index.html that only returns the index.html file
@app.route('/')
def index():
    return render_template('index.html')