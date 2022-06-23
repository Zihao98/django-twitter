from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # called when each test is called
        self.client = APIClient()
        self.user = self.createUser(
            username='unittest',
            email='unittest@gmail.com',
            password='unittest',
        )

    def createUser(self, username, email, password):
        # not using User.objects.create()
        # as password needs to be encrypted, username and email need normalization
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # starting with test_
        # test must use post not get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'unittest',
        })
        # login failed，http status code returns 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # used post but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # not yet logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # correat password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'unittest',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'unittest@gmail.com')
        # already logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'unittest',
        })
        # already logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # use get
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # use post successfully logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': 'any password',
        }
        # use get
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # password too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # username too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@gmail.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # login successfully
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)