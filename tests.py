import unittest
from app import create_app
from app import db
from api.models import User, Offer


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.app = create_app('config.TestingConfig')
        self.app.app_context().push()
        self.db.create_all(app=self.app)
        self.client = self.app.test_client()
        super(BaseTestCase, self).setUp()

    def tearDown(self):
        self.db.session.rollback()
        self.db.drop_all()
        super(BaseTestCase, self).tearDown()


class JobOfferTest(BaseTestCase):

    def setUp(self):
        super(JobOfferTest, self).setUp()
        # Create a user before every test
        self.user = User(username="username", password="password")
        self.user.create()

    def test_get_offer(self):
        # Create an offer in the database to retreive
        offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=self.user.id
        )
        offer.create()
        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            self.user.id,
            offer.id
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertEqual(response.json["title"], "Backend Engineer")
        self.assertEqual(response.json["description"], "Build a RESTful API")
        self.assertEqual(len(response.json["skills_list"]), 3)
        self.assertIsNotNone(response.json["creation_date"])
        self.assertIsNotNone(response.json["modification_date"])

        # Test when offer or user IDs don't exist
        response = self.client.get("/api/v1/users/1/offers/12")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/api/v1/users/13/offers/1")
        self.assertEqual(response.status_code, 404)

    def test_get_all_offers(self):
        # Create offers
        for i in range(5):
            Offer(
                title="Backend Engineer{}".format(i),
                description="Build a RESTful API",
                skills_list=["python", "flask", "DevOps"],
                user_id=self.user.id
            ).create()
        response = self.client.get("/api/v1/users/{}/offers/".format(self.user.id))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertEqual(len(response.json["offers"]), 5)
        self.assertEqual(response.json["count"], 5)
        self.assertIsNotNone(response.json["offers"][0]["title"])
        self.assertIsNotNone(response.json["offers"][0]["description"])
        self.assertIsNotNone(response.json["offers"][0]["skills_list"])
        self.assertIsNotNone(response.json["offers"][0]["creation_date"])
        self.assertIsNotNone(response.json["offers"][0]["modification_date"])

        # Test when user ID doesn't exist
        response = self.client.get("/api/v1/users/5/offers/")
        self.assertEqual(response.status_code, 404)

    def test_create_offer(self):
        pass

    def test_update_offer(self):
        pass



if __name__ == '__main__':
    unittest.main()