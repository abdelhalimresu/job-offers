import unittest
from app import create_app
from app import db
from api.models import User


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.db = db
        self.app = create_app('config.TestingConfig')
        self.app.app_context().push()
        self.db.create_all(app=self.app)
        self.client = self.app.test_client()

    def tearDown(self):
        self.db.session.rollback()
        self.db.drop_all()
        super(BaseTestCase, self).tearDown()


class ApiTest(BaseTestCase):

    def test_create_offer(self):
        user = User(username="resu", password="resu")
        user.create()
        user = User.query.first()
        self.assertEqual(user.username, "resu")


if __name__ == '__main__':
    unittest.main()