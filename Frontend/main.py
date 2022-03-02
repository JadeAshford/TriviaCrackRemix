from flask import Flask, render_template

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

    @app.route('/join')
    def create_account(username=None, password=None):
        return render_template('create_account.html')


    app.run()



if __name__ == '__main__':
    main()