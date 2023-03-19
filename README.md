
You need the following environment variables set

```
SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS
FLASK_ADMIN_SWATCH
OPENAI_API_KEY
SECRET_KEY
STRIPE_API_KEY
STRIPE_PRICE_PRO
STRIPE_PRICE_BASIC
STRIPE_WEBHOOK_SECRET
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
```

Some can be set easily as
```
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
FLASK_ADMIN_SWATCH = 'cerulean'
SECRET_KEY = 'samba'
```

And the following need a bit more effort
```
OPENAI_API_KEY

STRIPE_API_KEY
STRIPE_PRICE_PRO
STRIPE_PRICE_BASIC
STRIPE_WEBHOOK_SECRET

GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
```

# Open Api key
Signup for open api and get a key

# Stripe keys and configuration
You must create two products, one for 7 USD and another for 20 USD
You must pick "Recurring"

In addition you must go to
```
Developers -> API Keys -> Publishable key
```
*Note*: There is both a test environment and a production environment on stripe

You also need to add a Webhook endpoint (whatever is the live URL for the API) and then take the `STRIPE_WEBHOOK_SECRET` for that endpoint once you make it

# Google keys
Configuring google is a nightmare

1. Go to the Google Developers Console and create a new project.

2. Enable the Google+ API in the API Library.

3. In the Credentials tab, create a new OAuth 2.0 client ID. **VERY COMPLEX SEE BELOW** for details

4. Set the application type to Web application.

5. Add the authorized JavaScript origins and redirect URIs for your Flask app.

6. Save the client ID and client secret generated by Google.

## Create OAuth Client Id
1.  Go to the Google Developers Console: [https://console.developers.google.com/](https://console.developers.google.com/)
2.  Click on the project for which you want to create a client ID, or create a new project.
3.  In the left navigation panel, click on "Credentials".
4.  On the Credentials page, click the "Create credentials" button and select "OAuth client ID".
5.  Choose the "Web application" application type.
6.  In the "Authorized redirect URIs" section, add the URL where you want users to be redirected after they authenticate with Google. This should be a URL in your Flask app, e.g. "[http://localhost:5000/google_callback](http://localhost:5000/google_callback)". **THIS MUST BE THE API URL**
7.  Click the "Create" button to create the client ID.
8.  You will now see your new client ID and client secret. Copy these values and save them somewhere secure, as you will need them later in your Flask app as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`