from crypt import methods
from flask import Flask, make_response, render_template, request, redirect, url_for

from markupsafe import escape
import requests

from sessions import LoginError, UserSessions

API_ROOT = 'http://54.205.150.68:3000/'






authed_users = []
# (username, cookie, start time)
# set a timeout, and remove users from authed_users if it is too old
sessions = UserSessions()

def main():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template("home.html")

    #Initial login page
    @app.route("/login", methods=['GET'])
    def login():
        # render_template("login.html")
        # response = redirect(url_for("do_that"))
        print('forming response')
        response = make_response(render_template('login.html'))
        print('setting user')

        print('user')
        print('setting cookie')
        response.set_cookie('YourSessionCookie', 'testuser')
        print('returning')
        return response

    #Login page after submitting login details
    @app.route("/login", methods=['POST'])
    def submit_login():
        print(request.get_json())
        username = request.get_json()['username']
        password = request.get_json()['password']

        # print(f'Username: {username}')
        # print(f'Password: {password}')

        try:
            print("Attempting login...")
            # TODO: Fix this line
            sessions.attempt_login(username, password)
        except LoginError:
            print("Login failure")
        return render_template("login.html")







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
        
        cookie = request.cookies.get('YourSessionCookie')
        if not cookie:
            return render_template('redirect_login.html')
        print(cookie)
        return cookie


    app.run()

if __name__ == '__main__':
    main()