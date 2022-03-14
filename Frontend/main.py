from crypt import methods
from flask import Flask, render_template, request, redirect, url_for

from markupsafe import escape
import requests

import sessions

API_ROOT = 'http://54.205.150.68:3000/'






authed_users = []
# (username, cookie, start time)
# set a timeout, and remove users from authed_users if it is too old
sessions = sessions.UserSessions()

def main():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template("home.html")

    #Initial login page
    @app.route("/login", methods=['GET'])
    def login():
        render_template("login.html")
        response = redirect(url_for("do_that"))
        response.set_cookie('YourSessionCookie', user.id)
        return response

    #Login page after submitting login details
    @app.route("/login", methods=['POST'])
    def submit_login(username, password):
        username = request.get_json
        password = request.get_json
        try:
            print("Attempting long...")
            sessions.attempt_login(username, password)
        except sessions.LoginError:
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

    app.run()

if __name__ == '__main__':
    main()