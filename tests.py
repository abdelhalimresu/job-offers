# Built-in
import unittest
import hashlib

# Project imports
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
        self.user = User(username="username")
        self.user.create(password="password")

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
        offer_data = {
            'title': 'Backend Engineer',
            'skills_list': ['python', 'flask', 'DevOps'],
            'description': 'Build a RESTful API'
        }
        response = self.client.post(
            "/api/v1/users/{}/offers/".format(self.user.id),
            json=offer_data
        )
        self.assertEqual(response.status_code, 201)
        offer = Offer.query.filter_by(title='Backend Engineer', user_id=self.user.id).first()
        self.assertIsNotNone(offer)
        self.assertEqual(offer.description, "Build a RESTful API")
        self.assertEqual(offer.skills_list, ['python', 'flask', 'DevOps'])

        # Test with no data
        response = self.client.post("/api/v1/users/{}/offers/".format(self.user.id))
        self.assertEqual(response.status_code, 400)

        # Test with non-existent user id
        response = self.client.post(
            "/api/v1/users/100/offers/",
            json=offer_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid user id'})

        # Test with missing fields
        offer_data.pop("title", None)
        response = self.client.post(
            "/api/v1/users/{}/offers/".format(self.user.id),
            json=offer_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'title': ['Missing data for required field.']})

    def test_update_offer(self):
        # Create an offer in the database to update
        offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=self.user.id
        )
        offer.create()
        old_modification_date = offer.modification_date
        response = self.client.put(
            "/api/v1/users/{}/offers/{}".format(self.user.id, offer.id),
            json={
                "description": "Build a RESTful API with flask"
            }
        )
        self.assertEqual(response.status_code, 200)
        offer = Offer.query.first()
        self.assertEqual(offer.description, "Build a RESTful API with flask")
        self.assertGreater(offer.modification_date, old_modification_date)
        
        # Test with no data
        response = self.client.put("/api/v1/users/{}/offers/{}".format(self.user.id, offer.id))
        self.assertEqual(response.status_code, 400)

        # Test with non-existent offer id
        response = self.client.put(
            "/api/v1/users/{}/offers/12".format(self.user.id),
            json={
                "description": "Build a RESTful API with flask"
            }
        )
        self.assertEqual(response.status_code, 404)

        # Test with non-existent user id
        response = self.client.put(
            "/api/v1/users/12/offers/{}".format(offer.id),
            json={
                "description": "Build a RESTful API with flask"
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'message': 'Invalid user id'})

    def test_delete_offer(self):
        # Create an offer in the database to delete
        offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=self.user.id
        )
        offer.create()
        response = self.client.delete("/api/v1/users/{}/offers/{}".format(self.user.id, offer.id))
        self.assertEqual(response.status_code, 200)

        # Test with wrong user
        response = self.client.delete("/api/v1/users/12/offers/{}".format(offer.id))
        self.assertEqual(response.status_code, 404)

        # Test delete again
        response = self.client.delete("/api/v1/users/{}/offers/{}".format(self.user.id, offer.id))
        self.assertEqual(response.status_code, 404)


class UserTest(BaseTestCase):

    def test_register(self):
        user_data = {
            'username': 'abdelhalim',
            'password': 'pass'
        }
        response = self.client.post(
            "/api/v1/users/register",
            json=user_data
        )
        user = User.query.first()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"username": user.username, "id": user.id})
        self.assertEqual(user.username, "abdelhalim")
        self.assertEqual(user.hashed_password, hashlib.md5(bytes("pass", "utf-8")).hexdigest())

    def test_user_login(self):
        user = User(username="abdelhalim")
        user.create(password="password")
        user_id = user.id

        response = self.client.post(
            "/api/v1/users/login",
            json={"username": "abdelhalim", "password": "password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], user_id)
        self.assertIsNotNone(response.json["token"])

        # test with no data
        response = self.client.post(
            "/api/v1/users/login"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'No username/password provided'})

        # test with with wrong credentials
        response = self.client.post(
            "/api/v1/users/login",
            json={"username": "abdelhalim", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json,{'message': 'Invalid username/password'})



if __name__ == '__main__':
    unittest.main()