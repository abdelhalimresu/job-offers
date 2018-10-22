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
        self.header = {
            "Authorization" : "JWT {}".format(self.user.generate_token())
        }

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
        ), headers=self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertEqual(response.json["title"], "Backend Engineer")
        self.assertEqual(response.json["description"], "Build a RESTful API")
        self.assertEqual(len(response.json["skills_list"]), 3)
        self.assertIsNotNone(response.json["creation_date"])
        self.assertIsNotNone(response.json["modification_date"])
        
        # Test when offer or user IDs don't exist
        response = self.client.get("/api/v1/users/1/offers/12", headers=self.header)
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/api/v1/users/13/offers/1", headers=self.header)
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
        response = self.client.get("/api/v1/users/{}/offers/".format(self.user.id), headers=self.header)
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
        response = self.client.get("/api/v1/users/5/offers/", headers=self.header)
        self.assertEqual(response.status_code, 404)

    def test_create_offer(self):
        offer_data = {
            'title': 'Backend Engineer',
            'skills_list': ['python', 'flask', 'DevOps'],
            'description': 'Build a RESTful API'
        }
        response = self.client.post(
            "/api/v1/users/{}/offers/".format(self.user.id),
            json=offer_data, headers=self.header
        )
        self.assertEqual(response.status_code, 201)
        offer = Offer.query.filter_by(title='Backend Engineer', user_id=self.user.id).first()
        self.assertIsNotNone(offer)
        self.assertEqual(offer.description, "Build a RESTful API")
        self.assertEqual(offer.skills_list, ['python', 'flask', 'DevOps'])

        # Test with no data
        response = self.client.post("/api/v1/users/{}/offers/".format(self.user.id), headers=self.header)
        self.assertEqual(response.status_code, 400)

        # Test with non-existent user id
        response = self.client.post(
            "/api/v1/users/100/offers/",
            json=offer_data, headers=self.header
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'message': 'Unauthorized'})

        # Test with missing fields
        offer_data.pop("title", None)
        response = self.client.post(
            "/api/v1/users/{}/offers/".format(self.user.id),
            json=offer_data, headers=self.header
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
            },
            headers=self.header
        )
        self.assertEqual(response.status_code, 200)
        offer = Offer.query.first()
        self.assertEqual(offer.description, "Build a RESTful API with flask")
        self.assertGreater(offer.modification_date, old_modification_date)
        
        # Test with no data
        response = self.client.put(
            "/api/v1/users/{}/offers/{}".format(self.user.id, offer.id),
            headers=self.header
        )
        self.assertEqual(response.status_code, 400)

        # Test with non-existent offer id
        response = self.client.put(
            "/api/v1/users/{}/offers/12".format(self.user.id),
            json={
                "description": "Build a RESTful API with flask"
            },
            headers=self.header
        )
        self.assertEqual(response.status_code, 404)


    def test_delete_offer(self):
        # Create an offer in the database to delete
        offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=self.user.id
        )
        offer.create()
        response = self.client.delete(
            "/api/v1/users/{}/offers/{}".format(self.user.id, offer.id),
            headers=self.header
        )
        self.assertEqual(response.status_code, 200)

        # Test delete again
        response = self.client.delete(
            "/api/v1/users/{}/offers/{}".format(self.user.id, offer.id),
            headers=self.header
        )
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

class AuthTest(BaseTestCase):

    def test_token_authentication(self):
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

        token = response.json["token"]
        # Create an offer in the database to check if user can get with the token
        offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=user_id
        )
        offer.create()

        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            user_id,
            offer.id
        ), headers={"Authorization": "JWT " + token})

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertEqual(response.json["title"], "Backend Engineer")

        # Test with no header
        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            user_id,
            offer.id
        ))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Authorization header is expected"})

        # Test with wrong header
        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            user_id,
            offer.id
        ), headers={"Authorization": "my token: " + token})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Authorization header must 'JWT token'"})

        # Test with wrong token
        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            user_id,
            offer.id
        ), headers={"Authorization": "JWT " + "wrongtoken"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Invalid Token"})


class PermissionTest(BaseTestCase):

    def setUp(self):
        super(PermissionTest, self).setUp()
        # Create a user1 and user2 before every test
        self.user1 = User(username="user1")
        self.user1.create(password="pass1")
        self.token1 = {
            "Authorization" : "JWT {}".format(self.user1.generate_token())
        }
        self.user2 = User(username="user2")
        self.user2.create(password="pass2")
        self.token2 = {
            "Authorization" : "JWT {}".format(self.user2.generate_token())
        }
        # Create offer by user1
        self.offer = Offer(
            title="Backend Engineer",
            description="Build a RESTful API",
            skills_list=["python", "flask", "DevOps"],
            user_id=self.user1.id
        )
        self.offer.create()

    def test_user2_get_permissions(self):
        # User2 can read user1 offers
        response = self.client.get("/api/v1/users/{}/offers/{}".format(
            self.user1.id,
            self.offer.id
        ), headers=self.token2)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/v1/users/{}/offers/".format(
            self.user1.id
        ), headers=self.token2)
        self.assertEqual(response.status_code, 200)

    def test_user2_create_permissions(self):
        # User2 cannot create offers in user1 endpoint
        offer_data = {
            'title': 'Frontend Engineer',
            'skills_list': ['vue', 'react', 'html'],
            'description': 'Build a Frontends'
        }
        response = self.client.post(
            "/api/v1/users/{}/offers/".format(self.user1.id),
            json=offer_data, headers=self.token2
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'message': 'Unauthorized'})

    def test_user2_edit_permissions(self):
        # User2 cannot edit offers in user1 endpoint
        response = self.client.put(
            "/api/v1/users/{}/offers/{}".format(self.user1.id, self.offer.id),
            json={
                "description": "Build a RESTful API with flask"
            },
            headers=self.token2
        )
        self.assertEqual(response.status_code, 401)

    def test_user2_delete_permissions(self):
        # User2 cannot delete offers in user1 endpoint
        response = self.client.delete(
            "/api/v1/users/{}/offers/{}".format(self.user1.id, self.offer.id),
            headers=self.token2
        )
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()