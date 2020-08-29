import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('root:123@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_categories_route(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['categories'])
        self.assertGreater(len(data['categories']), 0)

    def test_questions_route(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['categories'])
        self.assertTrue(len(data['categories']))
        self.assertIsNotNone(data['questions'])
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(len(data['questions']), 0)

    def test_post_questions_route(self):
        req_body = {
            'question': 'whats app ?',
            'answer': 'I am fine',
            'category': '1',
            'difficulty': '2'
        }
        res = self.client().post('/questions', json=req_body)

        self.assertEqual(res.status_code, 200)

        req_body = {
            'question': '',
            'answer': '',
            'category': '1',
            'difficulty': '2'
        }

        res = self.client().post('/questions', json=req_body)

        self.assertEqual(res.status_code, 422)

    def test_delete_questions_route(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions(self):
        res = self.client().post('/questions-search', json={'searchTerm': 'w'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['questions']), 0)
        self.assertEqual(len(data['questions']), data['totalQuestions'])

        res = self.client().post('/questions-search', json={'searchTerm': 'Not found question !!'})
        self.assertEqual(res.status_code, 404)

    def test_get_questions_by_cat_id(self):
        res = self.client().get('/categories/1/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['questions']), 0)
        self.assertEqual(len(data['questions']), data['totalQuestions'])
        self.assertEqual(data['currentCategory'], 1)

        res = self.client().get('/categories/1000/questions')

        self.assertEqual(res.status_code, 404)

    def test_play_quiz(self):
        res = self.client().get('/categories/1/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])

        res = self.client().get('/categories/1000/questions')

        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
