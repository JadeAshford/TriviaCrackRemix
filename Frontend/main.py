from cgi import test
from crypt import methods
from distutils.dep_util import newer_group
from flask import Flask, make_response, render_template, request, redirect, session, url_for, flash

from markupsafe import escape
import requests
import json

from sessions import LoginError, UserSessions
from quizzes import Quiz, Question, get_quizes_by_user_id

API_ROOT = 'http://54.205.150.68:3000/'

def get_next_user_id() -> int:
    endpoint = API_ROOT + 'user?select=user_id&order=user_id.desc&limit=1'
    return requests.get(endpoint).json()[0]['user_id'] + 1

def get_all_users() -> list:
    endpoint = API_ROOT + 'user?order=user_id.asc'
    return requests.get(endpoint).json()

def get_single_user(user_id):
    endpoint = API_ROOT + f'user?order=user_id.asc&user_id=eq.{user_id}'
    return requests.get(endpoint).json()

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
        cookie = request.cookies.get('session')

        # sessions.is_valid_session(cookie)
        if not cookie:
            return render_template('create_user.html')
        if sessions.is_valid_session('cookie'):
            return render_template('redirect_dashboard.html')
        return render_template('redirect_login.html')

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
        if not cookie:
            return render_template('login.html')

        if not sessions.is_valid_session(cookie):
            return render_template('login.html')

        return render_template('redirect_dashboard.html', )
        
    #Login page after submitting login details
    @app.route("/login", methods=['POST'])
    def submit_login():
        username = request.form['username']
        password = request.form['password']

        try:
            sessions.attempt_login(username, password)
        except LoginError:
            return render_template('login.html', failed_login=1)
        
        response = make_response(render_template('redirect_dashboard.html'))
        cookie_set = sessions.attempt_login(username, password)
        response.set_cookie('session', cookie_set.cookie)
        return response


    #What should we put here? TODO
    @app.route("/dashboard")
    def dashboard():
        cookie = request.cookies.get('session')
        logged_in = sessions.is_valid_session(cookie)

        if not cookie:
            return render_template('redirect_login.html')

        if not logged_in:
            return render_template('redirect_login.html')

        if sessions.check_admin(cookie):
            return render_template('redirect_admin.html')

        user_id = sessions.get_user_id_by_cookie(cookie)
        quizzes = get_quizes_by_user_id(user_id)
        return render_template("dashboard.html", username=sessions.get_username_by_cookie(cookie), is_logged_in=logged_in, quizzes=quizzes)

    #Initial quiz creation page
    @app.route('/create_quiz', methods=['GET'])
    def create_quiz():
        cookie = request.cookies.get('session')
        if not cookie or not sessions.is_valid_session(cookie):
            print('INVALID COOKIE!')
            return render_template('redirect_login.html')

        return render_template('create_quiz.html')

    #Send created quiz data to database
    @app.route('/create_quiz', methods=['POST'])
    def post_quiz():
        print(f'Received New quiz creation: \n{request.form["quiz_name"]}')

        # get the next highest quiz ID
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
        test_question['answers'].append('Purple')
        test_question['answers'].append('Pink')
        questions.append(test_question)

        test_question['text'] = 'What is Kate\'s favorite color?'
        questions.append(test_question)

        test_question['text'] = 'What color is Red and Blue combined?'
        questions.append(test_question)
        
        print(questions)
        return render_template('take_quiz_by_link.html', questions=questions, quiz_id=quiz_id)

    @app.route('/quiz/<quiz_id>', methods=['POST'])
    def get_quiz_score(quiz_id):
        return 'Received quiz score!'

    @app.route('/admin', methods=['GET'])
    def admin():
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')

        logged_in = sessions.is_valid_session(cookie)
        if not sessions.check_admin(cookie):
            return render_template('redirect_dashboard.html')

        # get a list of all users
        users = get_all_users()
        return render_template('admin.html', is_logged_in=logged_in, users=users)




    @app.route('/admin/delete/<user_id>', methods=['POST'])
    def admin_delete_user(user_id):
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        logged_in = sessions.is_valid_session(cookie)
        if not sessions.check_admin(cookie):
            return render_template('redirect_dashboard.html')

        # http://54.205.150.68:3000/user?user_id=eq.100
        endpoint = API_ROOT + f'user?user_id=eq.{user_id}'
        response = requests.delete(endpoint)
        return render_template('redirect_admin.html')

    @app.route('/admin/user/role/', methods=['POST'])
    def admin_modify_user_role():
        cookie = request.cookies.get('session')
        if not cookie:
            return render_template('redirect_login.html')
        logged_in = sessions.is_valid_session(cookie)
        if not sessions.check_admin(cookie):
            return render_template('redirect_dashboard.html')
        role = request.form["new_role"]
        user_id = request.form['user_id']
        user = get_single_user(user_id)[0]
        user['role'] = role
        endpoint = API_ROOT + 'user'
        to_send = {}
        to_send['user_id'] = user['user_id']
        to_send['username'] = user['username']
        to_send['password_hash'] = user['password_hash']
        to_send['role'] = role
        to_send['flagged_count'] = user['flagged_count']
        to_send = json.dumps([to_send])
        print(f'Sending: {to_send}')
        response = requests.post(endpoint, to_send, headers={"Prefer": "resolution=merge-duplicates"})
        print(response)
        print(response.text)
        return render_template('redirect_admin.html')





    @app.route('/logout')
    def logout():
        cookie = request.cookies.get('session')
        if cookie:
            sessions.logout_session(cookie)

        response = make_response(render_template('redirect_login.html'))
        response.delete_cookie('session')
        return response
    @app.route('/create_question')
    def create_question():
        pass

    app.run()

if __name__ == '__main__':
    main()





    # @app.route('/<table>/<username>')
    # def name_given(table=None, username=None):
    #     current_user = 'Test User654645'

        
    #     response = requests.get(API_ROOT + 'user' + f'?username=eq.{current_user}')
    #     print('**************************************')
    #     print(response.json())
    #     #user = response.json()

    #     try:
    #         username = response.json()[0]['username']
    #     except TypeError:
    #         username = None
    #     print('**************************************')
    #     return render_template('layout.html', username=username)


    # @app.route('/test')
    # def test_cookies():
    #     print('received request')
    #     cookie = request.cookies.get('session')
    #     if not cookie:
    #         return render_template('redirect_login.html')
    #     print(f'attemtping login with cookie: {cookie}')
    #     current_user = sessions.attempt_login('1', '0')
        
    #     print(f'Current User: {current_user}')
    #     return cookie

    # @app.route('/cookies')
    # def get_sessions():
    #     print(sessions)
    #     return str(sessions)