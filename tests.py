from unittest import TestCase
from werkzeug.datastructures import MultiDict, ImmutableMultiDict

from app import app
from models import db, User, Feedback

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """ Test Case for User views """

    def setUp(self):
        """ Add sample users """

        all_users = User.query.all()
        for test_user in all_users:
            db.session.delete(test_user)
        all_feedback = Feedback.query.all()
        for test_feedback in all_feedback:
            db.session.delete(test_feedback)
        user_1 = User.register(username="pieguy123",password="password",email="iluvpie@gmail.com",first_name="Tom",last_name="Hanks")
        user_2 = User.register(username="cakedude123",password="batman",email="iluvcake@gmail.com",first_name="Frida",last_name="Kahlo")
        user_3 = User.register(username="pineapple123",password="qwerty",email="iluvpineapple@gmail.com",first_name="Simon",last_name="Says")
        for user in [user_1, user_2, user_3]:
            db.session.add(user)
        db.session.commit()
        feedback_1 = Feedback(title="Soccer Game Was Too Long",content="Should have ended after the first goal",username="pieguy123")
        feedback_2 = Feedback(title="No more silly string", content="Takes too long to clean up.", username="cakedude123")
        feedback_3 = Feedback(title="More silly string!", content="I ran out before the first goal", username="pieguy123")
        for feedback in [feedback_1, feedback_2, feedback_3]:
            db.session.add(feedback)
        db.session.commit()

    def tearDown(self):
        """ Tear Down """

        db.session.rollback()
    
    def login(self, client):
        user_credentials = {
            'username': 'pieguy123',
            'password': 'password'
        }
        client.post("/login", data=user_credentials, follow_redirects=True)

    def test_register_user(self):
        with app.test_client() as client:
            registration = {
                'username': 'test-user',
                'password': 'test-password',
                'email': 'test-email@aol.com',
                'first_name': 'test_1',
                'last_name': 'test_2'
            }
            resp = client.post("/register", data=registration, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("test-user",html)
            self.assertIn("test-email@aol.com",html)
            self.assertIn("test_1",html)
            self.assertIn("test_2",html)
            
    def test_login_user(self):
        with app.test_client() as client:
            user_credentials = {
                'username': 'pieguy123',
                'password': 'password'
            }
            resp = client.post("/login", data=user_credentials, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("pieguy123",html)
    
    def test_add_feedback(self):
        with app.test_client() as client:
            self.login(client)
            new_feedback = {
                "title": "This is an added test feedback title",
                "content": "This is the added test feedback content",
            }
            resp = client.post('/users/pieguy123/feedback/add', data=new_feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("This is an added test feedback title",html)
            self.assertIn("This is the added test feedback content",html)
    
    def test_edit_feedback(self):
        with app.test_client() as client:
            self.login(client)
            active_user = User.query.filter_by(username="pieguy123").first()
            current_feedback = active_user.feedback[0]
            edited_feedback = {
                "title": "This is an edited test feedback",
                "content": "This is edited test feedback content",
            }
            resp = client.post(f"/feedback/{current_feedback.id}/update", data=edited_feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("This is an edited test feedback",html)
            self.assertIn("This is edited test feedback content",html)
    
    def test_delete_feedback(self):
        with app.test_client() as client:
            self.login(client)
            active_user = User.query.filter_by(username="pieguy123").first()
            current_feedback = active_user.feedback[0]
            resp = client.post(f"/feedback/{current_feedback.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertNotIn("Soccer game was too long",html)
            self.assertIn("More silly string!",html)
    
    def test_unauthorized_add_feedback(self):
        with app.test_client() as client:
            self.login(client)
            new_feedback = {
                "title": "This is an added test feedback title",
                "content": "This is the added test feedback content",
            }
            resp = client.post('/users/cakedude123/feedback/add', data=new_feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertNotIn("This is an added test feedback title",html)
            self.assertNotIn("This is the added test feedback content",html)
            self.assertIn("You do not have permission to add feedback for this user",html)
    
    def test_unauthorized_edit_feedback(self):
        with app.test_client() as client:
            self.login(client)
            active_user = User.query.filter_by(username="cakedude123").first()
            current_feedback = active_user.feedback[0]
            edited_feedback = {
                "title": "This is an edited test feedback",
                "content": "This is edited test feedback content",
            }
            resp = client.post(f"/feedback/{current_feedback.id}/update", data=edited_feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertNotIn("This is an edited test feedback",html)
            self.assertNotIn("This is edited test feedback content",html)
            self.assertIn("You do not have permission to edit",html)
    
    def test_unauthorized_delete_feedback(self):
        with app.test_client() as client:
            self.login(client)
            active_user = User.query.filter_by(username="cakedude123").first()
            current_feedback = active_user.feedback[0]
            resp = client.post(f"/feedback/{current_feedback.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("No more silly string",html)
            self.assertIn("Takes too long to clean up.",html)
            self.assertIn("You do not have permission to delete this feedback",html)
    
    def test_unauthorized_delete_user(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.post(f"/users/cakedude123/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("You do not have permission to delete this account",html)
            resp = client.get("/users/cakedude123", follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("cakedude123",html)
            self.assertIn("No more silly string",html)
            self.assertIn("Takes too long to clean up.",html)