from flask import Flask, render_template, request

from markupsafe import escape
import requests


API_ROOT = 'http://54.205.150.68:3000/'


authed_users = []

def main():
    app = Flask(__name__)

    @app.route('/')
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