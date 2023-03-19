from urllib.parse import urlencode
from models import User, Prompt
from openapi import open_ai_completion
from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import stripe
import datetime
from flask import url_for, redirect, request, jsonify, session
from google.oauth2 import id_token
from google.auth.transport import requests
import secrets


stripe.api_key = app.config['STRIPE_API_KEY']

# create jwt token
def create_token(user_id):
    token = jwt.encode({'user_id': user_id}, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# decode jwt token
def decode_token(token):
    try:
        user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
    except Exception as e:
        return None
    return user_id

# method to call open_ai_completion and save the prompt and response to the database
def generate_response(prompt_text, user_id):
    # call the openai api to generate a response
    response = open_ai_completion(prompt_text)
    # save the prompt and response to the database
    prompt = Prompt(prompt_text=prompt_text, response_text=response, user_id=user_id)
    db.session.add(prompt)
    db.session.commit()
    return response

# sign up with email and password
def sign_up(email, password):
    # check if the email is already in the database
    user = User.query.filter_by(email=email).first()
    if user:
        return False
    
    # check if the email is a valid email string
    if not email or '@' not in email:
        return False
    
    # hash the password
    password = generate_password_hash(password, method='sha256')

    # if the email is not in the database, add the user to the database
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return True

# login with email and password and return a jwt token
def login(email, password):
    # check if the email is in the database
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    
    # check if the password is correct
    if check_password_hash(user.password, password):
        return create_token(user.user_id)
    return False

# google login
def google_login(token):
    state = secrets.token_urlsafe(16)
    session['state'] = state
    params = {
        'response_type': 'code',
        'client_id': app.config.get('CLIENT_ID'),
        'redirect_uri': url_for('google_callback', _external=True),
        'scope': 'openid email profile',
        'state': state
    }
    # Redirect the user to the authorization page.
    authorization_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)
    return redirect(authorization_url)


def google_callback():
    if request.args.get('state') != session['state']:
        return redirect(url_for('index'))
        
    # Exchange the authorization code for an access token.
    authorization_code = request.args.get('code')
    token_params = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': app.config.get('GOOGLE_CLIENT_ID'),
        'client_secret': app.config.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': url_for('google_callback', _external=True)
    }
    response = requests.requests.post('https://www.googleapis.com/oauth2/v4/token', data=token_params)
    token_data = response.json()
    access_token = token_data['access_token']
    # Retrieve the user's information using the access token.
    userinfo_response = requests.requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': 'Bearer ' + access_token})
    userinfo = userinfo_response.json()
    # Verify the ID token to ensure the user is authenticated.
    idinfo = id_token.verify_oauth2_token(token_data['id_token'], requests.Request(), app.config.get('CLIENT_ID'),)
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')
    
    google_id = idinfo['sub']
    google_name = idinfo['name']
    google_email = idinfo['email']
    # store the user's Google ID, name, and email in the session
    session['google_id'] = google_id
    session['google_name'] = google_name
    session['google_email'] = google_email    
    
    # Check if the user already exists in the database.
    user = User.query.filter_by(email=userinfo['email']).first()
    if not user:
        # Create a new user.
        user = User(email=userinfo['email'])
        db.session.add(user)
        db.session.commit()

    return create_token(user.user_id)


    


# create payment method for stripe. It accepts a user, card info and billing details
def create_payment_method(card, billing_details):
    # create a payment method with the card info
    payment_method = stripe.PaymentMethod.create(
        type='card',
        card=card,
        billing_details=billing_details
    )

    return payment_method

# create_stripe_customer accepts payment_method_id and user
def create_stripe_customer(payment_method_id, user):
    # create a customer with the payment_method_id
    customer = stripe.Customer.create(
        payment_method=payment_method_id,
        email=user.email,
        invoice_settings={
            'default_payment_method': payment_method_id
        }
    )

    return customer

# create a basic subscription for the user
def subscribe_basic(user, card, billing_details):
    # create a payment method with the card info
    payment_method = create_payment_method(card, billing_details)
    # create a customer with the payment_method_id
    customer = create_stripe_customer(payment_method.id, user)
    # create a subscription for the customer
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[
            {
                'price': app.config['STRIPE_PRICE_BASIC'],
            },
        ],
        expand=['latest_invoice.payment_intent'],
    )
    # update the user's subscription_id and customer_id
    user.subscription_type = 'basic'
    user.subscription_id = subscription.id
    user.customer_id = customer.id
    db.session.commit()
    return True

# create a pro subscription for the user
def subscribe_pro(user, card, billing_details):
    # create a payment method with the card info
    payment_method = create_payment_method(user, card, billing_details)
    # create a customer with the payment_method_id
    customer = create_stripe_customer(payment_method.id, user)
    # create a subscription for the customer
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[
            {
                'price': app.config['STRIPE_PRICE_PRO'],
            },
        ],
        expand=['latest_invoice.payment_intent'],
    )
    # update the user's subscription_id and customer_id
    user.subscription_type = 'pro'
    user.subscription_id = subscription.id
    user.customer_id = customer.id
    db.session.commit()
    return True

# cancel the user's subscription
def cancel_subscription(user):
    # cancel the user's subscription
    subscription = stripe.Subscription.delete(user.subscription_id)
    # update the user's subscription_id and customer_id
    user.subscription_type = None
    user.subscription_id = None
    user.customer_id = None
    db.session.commit()
    return True

# webhook for stripe to handle payment succeeded/failed
def process_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config.get('STRIPE_WEBHOOK_SECRET')
        )    

        # Handle the event
        if event['type'] == 'invoice.payment_succeeded':
            email = event['data']['object']['customer_email']
            user = User.query.filter_by(email=email).first()

            if user.subscription_type == 'basic':
                user.remaining_uses += 10

            period_end = event['data']['object']['period_end']
            # convert integer to datetime
            period_end = datetime.datetime.fromtimestamp(period_end)
            user.next_payment_date = period_end
    
    except Exception as e:
        print(e)

# prompt the openai api to generate a response
def get_open_ai_completion(user, prompt_text):
    # check if the user has a subscription
    if not user.subscription_type:
        return False
    
    # check if the user has remaining uses
    if user.remaining_uses <= 0 and user.subscription_type != 'pro':
        return False

    # call the openai api to generate a response
    response = open_ai_completion(prompt_text)
    # save the prompt and response to the database
    prompt = Prompt(prompt_text=prompt_text, response_text=response, user_id=user.user_id)
    db.session.add(prompt)
    db.session.commit()
    # decrement the user's remaining uses

    if user.subscription_type != 'pro':
        user.remaining_uses -= 1

    db.session.commit()
    return response

# get the user's prompts and responses from the database ordered by descending date
def get_user_prompts(user):
    prompts = Prompt.query.filter_by(user_id=user.user_id).order_by(Prompt.created_at.desc()).all()
    return prompts
