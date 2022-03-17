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
        self.cookie = self._generate_cookie() # set cookie to hash of username and login time

    def _generate_cookie(self) -> str:
        return f'{self.username}{self.active_time}'

    def is_logged_in(self) -> bool:
        duration = (datetime.now() - self.active_time).total_seconds()
        print(duration)
        if duration < LOGIN_TIMEOUT:
            self._activity()   
        else:
            pass

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
        raise LoginError

    def logout_session(self, cookie):
        for i in len(self.logged_in_users):
            if i.cookie == cookie:
                self.logged_in_users.remove[i]
        return

    def get_username_by_cookie(self, cookie) -> str:
        # print(f'Received cookie: {cookie}')
        for i in range(0, len(self.logged_in_users)):
            if self.logged_in_users[i].cookie == cookie:
                # print(self.logged_in_users[i])
                return self.logged_in_users[i].username

    def check_admin(self, cookie) -> bool:
        print('checking cookie for admin')
        for i in range(0, len(self.logged_in_users)):
            print(f'users: {self}')
            if self.logged_in_users[i].cookie == cookie:
                print('cookie is valid')
                # Make api call to get roles of user
                # get the username from the cookie
                username = self.get_username_by_cookie(cookie)
                endpoint = self.API_ROOT + 'user' + f'?username=eq.{username}'
                # print(f'calling endpoint {endpoint}')
                response = requests.get(endpoint).json()[0]
                 
                print(f'RESPONSE:\n\t{response}')
                if response['role'] == 'admin':
                    return True
                else:
                    return False

            else:
                print('INVALID COOKE!')

    def _hash_password(self, password):
        return password

    def attempt_login(self, username: str, password: str) -> LoggedInUser:
        # make API call to database to check for username

        endpoint = self.API_ROOT + 'user' + f'?username=eq.{username}'
        api_response = requests.get(endpoint)
        # print(f'API RESPONSE: {api_response.json()}')
        if api_response.json():
            body = api_response.json()[0]
        else:
            raise LoginError

        if api_response.status_code == 200:
            # User exists in database
            if body["password_hash"] == self._hash_password(password):
                user = LoggedInUser(body['username'])
                self.logged_in_users.append(user)
                return user
                
            else:
                # password is incorrect
                raise LoginError
        else:
            # username does not exist
            raise LoginError


    def is_valid_session(self, cookie) -> bool:
        for i in range(0, len(self.logged_in_users)):
            if self.logged_in_users[i].cookie == cookie:
                return True
        return False

    def logout_session(self, cookie) -> None:
        for i in range(0, len(self.logged_in_users)):
            if self.logged_in_users[i].cookie == cookie:
                self.logged_in_users[i]
                return

    def __str__(self):
        # print(self.logged_in_users)
        to_return = ''
        for user in self.logged_in_users:
            to_return += 'user:' + str(user) + '\n'
            # print(to_return)
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