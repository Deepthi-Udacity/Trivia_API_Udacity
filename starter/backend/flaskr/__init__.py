import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category , db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def get_categories_dict():
  categories= Category.query.order_by(Category.id).all()
  categories_dict={}
  for category in categories:
    categories_dict[category.id]=category.type
  if len(categories) == 0:
    abort(404)
  return categories_dict

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
      )
      response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
      )
      return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  '''
    [GET all categories endpoint]
    Returns:
        categories: all categories
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
      return jsonify(
        {
          "success": True,
          "categories":get_categories_dict()
        })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  '''
    [GET all questions endpoint]
    Returns:
        questions : list of all questions paginated
        total_questions : number of total questions (integer)
        categories: all categories
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    if len(current_questions) == 0:
      abort(404)
    return jsonify(
      {
        "success": True,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
        "categories": get_categories_dict()
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
    [DELETE a  question endpoint]
    Path Param :
        question_id : integer
    Returns:
        deleted : deleted question id
        questions : list of all questions paginated
        total_questions : number of total questions (integer)
        categories: all categories
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      return jsonify(
        {
          "success": True,
          "deleted": question_id,
          "questions": current_questions,
          "total_questions": len(Question.query.all()),
          "categories": get_categories_dict()
        })
    except:
      abort(422)
  
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
    [POST Add a  question endpoint]
    Input :
        question : question
        answer : answer for the ques
        category : category to which the question belongs
        difficulty : difficulty rating of the ques
    Returns:
        created : created question id
  '''
  '''
    [POST Search a  question endpoint]
    Input :
        searchTerm : searchTerm
    Returns:
        questions : list of questions matching the search term , paginated
        total_questions : number of questions

  '''
  @app.route('/questions', methods=['POST'])
  def create_questions():
    body = request.get_json()
    question =  body.get("question", None)
    answer =  body.get("answer", None)
    category =  body.get("category", None)
    difficulty = body.get("difficulty",None)
    searchTerm = body.get("searchTerm",None)
    try:
      if searchTerm:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm)))
        current_questions = paginate_questions(request, selection)
        return jsonify(
          {
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection.all())
          })
      else:
        newQuestion = Question(question =question ,answer=answer,category=category,difficulty=difficulty)
        newQuestion.insert()
        return jsonify(
          {
            "success": True,
            "created": newQuestion.id
          })
    except:
            abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  '''
    [GET a  question by category endpoint]
    Path Param :
        category_id : integer
    Returns:
        questions : list of all questions paginated
        total_questions : number of total questions (integer)
        current_category: category to which the question belongs
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    
    selection = Question.query.filter_by(category=category_id).all()
    current_questions = paginate_questions(request, selection)
    if len(current_questions) == 0:
      abort(404)
    category= Category.query.filter_by(id=category_id).one_or_none()
    if category is None:
      abort(404)
    return jsonify(
      {
        "success": True,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
        "current_category" : category.type
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  '''
    [POST play quiz endpoint]
    Input :
        previous_questions : array of previously answered question
        quiz_category:
          id :  integer
          type : category type
    Returns:
        question : next question to be answered
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    previous_questions =  body.get("previous_questions", None)
    quiz_category =  body.get("quiz_category", None)

    if ((quiz_category is None) or (previous_questions is None)):
      abort(400)

    else:
      category_id = quiz_category['id']
    
    try:
      if category_id == 0:
        remaining_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        remaining_questions = Question.query.filter(Question.category==category_id,Question.id.notin_(previous_questions)).all()
        
      if len(remaining_questions) > 0:
        next_question = remaining_questions[random.randrange(0,len(remaining_questions),1)]
        return jsonify({
          "success": True,
          "question" : next_question.format()
        })
      else :
        return jsonify(
          {
            "success": True
          })
    except:
      abort(422)
    
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  # 404 - Resource Not found
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource Not found"
      }), 404

  # 422 - Unprocessable entry
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable entry"
    }), 422

  # 400 - Bad Request
  @app.errorhandler(400)
  def badrequest(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
      }), 400

  # 405 - Method Not allowed
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
        "error": 405,
        "message": "Method Not Allowed"
        }), 405

  # 500 - Internal Server Error
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
        "error": 500,
        "message": "Internal Server Error"
        }), 500

  if __name__ == "__init__":
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port , debug=True)

  return app

    