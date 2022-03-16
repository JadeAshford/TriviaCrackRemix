from cgi import test
from crypt import methods
from flask import Flask, make_response, render_template, request, redirect, session, url_for, flash

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
    @app.route("/admin")
    def profile_admin():
        return render_template("admin.html")

    #What should we put here? TODO
    @app.route("/dashboard")
    def dashboard():
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        username = sessions.get_username_by_cookie(cookie)
        print(f'Username: {username}')
        return render_template("dashboard.html", username=sessions.get_username_by_cookie(cookie))


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
        return render_template('create_user.html')


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

    #Initial quiz creation page
    @app.route('/create_quiz', methods=['GET'])
    def create_quiz(quiz_id):
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        return render_template('create_quiz.html')

    #Send created quiz data to database
    @app.route('/create_quiz', methods=['POST'])
    def post_quiz(quiz_id):
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        return "Quiz received!"

    @app.route('/quiz/<quiz_id>', methods=['GET'])
    def take_quiz(quiz_id):
        questions = []
        test_question = {}
        test_question['text'] = 'What color is the sky?'
        test_question['answers'] = []
        test_question['answers'].append('Blue')
        test_question['answers'].append('Red')
        test_question['answers'].append('Green')
        test_question['answers'].append('Pink')
        questions.append(test_question)
        questions.append(test_question)
        questions.append(test_question)
        print(questions)
        return render_template('take_quiz_by_link.html', questions=questions, quiz_id=quiz_id)

    @app.route('/quiz/<quiz_id>', methods=['POST'])
    def get_quiz_score(quiz_id):
        return 'Received quiz score!'

    @app.route('/admin')
    def admin():
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        return render_template('admin.html')

    @app.route('/logout')
    def logout():
        return "not yet implemented!"


    app.run()

if __name__ == '__main__':
    main()