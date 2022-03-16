from datetime import datetime
import string

import requests


LOGIN_TIMEOUT = 600 # number of seconds before a user is logged out due to inactivity


class LoginError(Exception):
    """Raised when the username or password is incorrect"""
    pass



class LoggedInUser:
    def __init__(self, username) -> None:
        self.username = username
        self.active_time = datetime.now()
        self.cookie = 'no cookie yet!' # set cookie to hash of username and login time
        print('logged in:')
        print(self.active_time)

    def is_logged_in(self) -> bool:
        duration = (datetime.now() - self.active_time).total_seconds()
        print(duration)
        if duration < LOGIN_TIMEOUT:
            self._activity()
            print('still logged in!')
            
        else:
            print('logged out due to timeout!')

    def _activity(self) -> None:
        self.active_time = datetime.now()
        
    def __str__(self) -> str:
        return f'user: \n\tUsername: {self.username}\n\tLast Activity: {self.active_time}\n Cookie: {self.cookie}'


class UserSessions:
    def __init__(self) -> None:
        self.logged_in_users = []
        self.API_ROOT = 'http://54.205.150.68:3000/'
        # self.logged_in_users.append(LoggedInUser('test_user'))
    def check_cookie(self, cookie) -> string:
        # Check based on cookie sent in request if the user is a currently logged in user
        for user in self.logged_in_users:
            if user.cookie == cookie:
                return user.username
        return ''

    def _hash_password(self, password):
        return password

    def attempt_login(self, username: str, password: str) -> LoggedInUser:
        # make API call to database to check for username

        # test block
        # username = '1'
        # password = '0'


        # end test block
        endpoint = self.API_ROOT + 'user' + f'?username=eq.{username}'



        api_response = requests.get(endpoint)
        # print(api_response.json())
        body = api_response.json()[0]

        # print(api_response.json())
        if api_response.status_code == 200:
            # User exists in database
            # api_response = api_response.json()
            print(body)
            if body["password_hash"] == self._hash_password(password):
                # Password is correct, add to logged in users and issue cookie
                self.logged_in_users.append(LoggedInUser(body['username']))
                print("logged in users:")
                for user in self.logged_in_users:
                    print(user)
            else:
                # password is incorrect
                raise LoginError
        else:
            # username does not exist
            raise LoginError





    def __str__(self):
        print(self.logged_in_users)
        to_return = ''
        for user in self.logged_in_users:
            to_return += 'user:' + str(user) + '\n'
            print(to_return)
        return to_return 

def main():
    # test = LoggedInUser('testuser')
    # test.is_logged_in()
    sessions = UserSessions()



    # Test a correct login
    sessions.attempt_login('Test User', 'Password Hash')


    # Test an incorrect password
    try:
        sessions.attempt_login('Test User', 'Password Hash1')
    except LoginError:
        print('caught incorrect password successfully')

    # Test an incorrect username
    try:
        sessions.attempt_login('Test User', 'Password Hash1')
    except LoginError:
        print('caught incorrect username successfully')


if __name__ == '__main__':
    API_ROOT = 'http://54.205.150.68:3000/'
    main()