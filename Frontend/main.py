from crypt import methods
from flask import Flask, make_response, render_template, request, redirect, url_for, flash

from markupsafe import escape
import requests

from sessions import LoginError, UserSessions

API_ROOT = 'http://54.205.150.68:3000/'



def get_next_user_id() -> int:
    return 6


authed_users = []
# (username, cookie, start time)
# set a timeout, and remove users from authed_users if it is too old
sessions = UserSessions()

def main():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template("home.html")

    #Initial create user page
    @app.route("/create_user", methods=['GET'])
    def create_user():
        #TODO: actually make work

        # If user is already logged in, redirect to dashboard
        cookie = request.cookies.get('session')
        if cookie:
            return render_template('redirect_dashboard.html')
        return render_template('create_user.html')

           
    @app.route("/create_user", methods=['POST'])
    def submit_create_user():
        cookie = request.cookies.get('session')
        if cookie:
            return render_template('redirect_dashboard.html')
        account_create_data = request.form
        print(f'username: {account_create_data["username"]}\npassword: {account_create_data["password"]}')

        # Send an API request to postgrest to insert a user
        endpoint = API_ROOT + 'user'
        to_send = {}
        to_send['user_id'] = get_next_user_id()
        to_send['username'] = account_create_data["username"]
        to_send['password_hash'] = account_create_data["password"]
        to_send['role'] = "user"
        to_send['flagged_count'] = 0
        response = requests.post(endpoint, to_send)

        if response.status_code == 201:
            # the user was added to the database successfully
            response = make_response(render_template('redirect_dashboard.html'))
            cookie_set = sessions.attempt_login(to_send['username'], to_send['password_hash'])
            response.set_cookie('session', cookie_set.cookie)
            return response
        elif response.status_code == 409:
            # the user already exists
            return render_template('create_user.html', creation_failed=1, message='Account already exists')
        else:
            # there was a failure to create the account
            return render_template('create_user.html', creation_failed=1, message='There was a general failure. Please try again')


    #Initial login page
    @app.route("/login", methods=['GET'])
    def login():

        cookie = request.cookies.get('session')
        if cookie:
            return render_template('redirect_dashboard.html')
        response = make_response(render_template('login.html'))

        # TODO: set 'testuser' to actual session value
        print('returning')
        return response

    #Login page after submitting login details
    @app.route("/login", methods=['POST'])
    def submit_login():
        # print('GOT POST REQUEST:')
        # print(request.form)
        # print(dir(request))
        # print(type(request))
        username = request.form['username']
        password = request.form['password']

        # print(f'Username: {username}')
        # print(f'Password: {password}')

        try:
            print("Attempting login...")
            # TODO: Fix this line
            sessions.attempt_login(username, password)
        except LoginError:
            print("Login failure")
            # flash('Login incorrect')
            return render_template('login.html', failed_login=1)
        
        # TODO: set a session cookie
        response = make_response(render_template('redirect_dashboard.html'))
        cookie_set = sessions.attempt_login(username, password)
        response.set_cookie('session', cookie_set.cookie)
        return response

    #Admin page accessible only after login FIXME
    @app.route("/profile/admin")
    def profile_admin():
        return render_template("admin.html")

    #Profile page accessible only after login FIXME
    @app.route("/profile")
    def profile():
        return render_template("profile.html")

    #What should we put here? TODO
    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")


    @app.route('/<table>/<username>')
    def name_given(table=None, username=None):
        current_user = 'Test User654645'

        
        response = requests.get(API_ROOT + 'user' + f'?username=eq.{current_user}')
        print('**************************************')
        print(response.json())
        #user = response.json()

        try:
            username = response.json()[0]['username']
        except TypeError:
            username = None
        print('**************************************')
        return render_template('layout.html', username=username)

    @app.route('/join', methods=['GET'])
    def create_account():
        print('redirecting...')
        return render_template('create_account.html')


    @app.route('/join', methods=['POST'])
    def create_account_api():
        print('received account!')
        print(request)
        # redirect to home now, with the current user logged in...

    @app.route('/test')
    def test_cookies():
        print('received request')
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        print(f'attemtping login with cookie: {cookie}')
        current_user = sessions.attempt_login('1', '0')
        
        print(f'Current User: {current_user}')
        return cookie

    @app.route('/cookies')
    def get_sessions():
        print(sessions)
        return str(sessions)
    app.run()

if __name__ == '__main__':
    main()