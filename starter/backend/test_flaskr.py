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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "What is Udacity Trivia Api",
            "answer": "Its a game",
            "category": 5,
            "difficulty": 1
            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test to get list of all categories successfully
    # Expected - 200 
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
    
    # Test to get list of all questions successfully
    # Questions should be paginated by 10 per page
    # Expected - 200
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    # Test to get error when user searches for invalid page number
    # Expected - 404
    def test_404_get_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not found")

    # Test to add a new question successfully
    # Expected - 200
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

    # Test to get an error when user inputs incorrect entry in request
    # Expected - 422
    def test_422_create_question_unprocessable(self):
        new_question=self.new_question 
        new_question['category']="Entertainment"
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable entry")

    # Test to an error when the method is not allowed
    # Expected - 405
    def test_405_question_creation_not_allowed(self):
        res = self.client().post("/questions/1000", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    # Test to get list of all questions filtered by searchTerm successfully
    # Expected - 200
    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm": "penicillin"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 1)

    # Test to get nothing displayed for a searchTerm thats not there in DB
    # Expected - 200
    def test_search_question_not_exists(self):
        res = self.client().post("/questions", json={"searchTerm": "hello"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"],0)
        self.assertEqual(len(data["questions"]), 0)

    # Test to get list of questions filtered by category successfully
    # Expected - 200
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], "Art")
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))    

    # Test to get an error when a invalid category is given
    # Expected - 404
    def test_404_category_not_found(self):
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not found")

    # Test to delete a question successfully
    # Expected - 200
    # Delete a different question in each attempt
    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    # Test to get an error when user tries to delete a question that 
    #does not exist
    # Expected - 200
    def test_422_delete_question_notFound(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable entry")

    # Test to play the quiz successfully
    # Expected - 200
    def test_play_quiz_success(self):
        input = {
            "previous_questions":[21,22],
            "quiz_category":{
                "type": "Science",
                "id": "1"
                }
            }
        res = self.client().post("/quizzes", json=input)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # Test to reach the end of the play
    # Expected - 200
    def test_play_quiz_game_over(self):
        input = {
            "previous_questions":[20,21,22],
            "quiz_category":{
                "type": "Science",
                "id": "1"
                }
            }
        res = self.client().post("/quizzes", json=input)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # Test to get an error when an incorrect input is given
    # Expected - 400
    def test_400_play_quiz_bad_request(self):
        input = {
            "quiz_category":{
                "type": "Science",
                "id": "1"
                }
            }
        res = self.client().post("/quizzes", json=input)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()