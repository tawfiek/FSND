import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = {categories[i].id: categories[i].type for i in range(0, len(categories), 1)}
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions', methods=['GET', 'POST'])
    def get_all_questions():
        if request.method == 'GET':
            page = request.args.get('page', default=1, type=int)
            questions = Question.query.all()
            formatted_questions = [q.format() for q in questions]
            categories = Category.query.all()

            formatted_categories ={categories[i].id: categories[i].type for i in range(0, len(categories), 1)}
            start = (page-1) * 10
            end = page * 10
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'categories': formatted_categories,
                'current_category': 1
            })
        elif request.method == 'POST':
            try:
                body = request.get_json()

                q = Question(question=body['question'],
                             answer=body['answer'],
                             category=body['category'],
                             difficulty=body['difficulty'])

                db.session.add(q)
                db.session.commit()
                return jsonify(q.format())
            except:
                db.session.rollback()
            finally:
                db.session.close()

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            Question.query.filter_by(id=question_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True})

    @app.route('/questions-search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body['searchTerm']
        search = "%{}%".format(search_term.lower())
        questions = Question.query\
            .filter(db.func.lower(Question.question).like(search)).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'questions': formatted_questions,
            'totalQuestions': len(formatted_questions),
            'currentCategory': 1
        })

    @app.route('/categories/<int:cat_id>/questions')
    def get_questions_by_cat_id(cat_id):
        questions = Question.query.filter_by(category=cat_id).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'questions': formatted_questions,
            'totalQuestions': len(formatted_questions),
            'currentCategory': cat_id
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        category = body['quiz_category']
        previous_questions = body['previous_questions']
        res_boy = get_random_question(category['id'], previous_questions)
        previous_questions.append(res_boy['question']['id'])

        return jsonify(res_boy)

    def get_random_question(cat_id: int, prev_questions):
        if cat_id > 0:
            questions = Question.query.order_by('id')\
                .filter_by(category=cat_id).all()
        else:
            questions = Question.query.order_by('id').all()

        formatted_questions = [q.format() for q in questions]
        no_of_questions = len(formatted_questions)
        number = random.randint(0, no_of_questions - 1)

        if len(prev_questions) < no_of_questions:
            for p in prev_questions:
                while formatted_questions[number]['id'] == p:
                    number = random.randint(0, no_of_questions - 1)

        return {
                'question': formatted_questions[number],
                'forceEnd': no_of_questions == len(prev_questions) +1
            }
    ''' 
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    return app
