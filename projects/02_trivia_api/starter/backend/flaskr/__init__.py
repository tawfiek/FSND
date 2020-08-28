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
        try:
            categories = Category.query.all()
            formatted_categories = {categories[i].id: categories[i].type for i in range(0, len(categories), 1)}

            if len(formatted_categories) ==0:
                abort(404)

            return jsonify({
                'success': True,
                'categories': formatted_categories
            })
        except:
            abort(400)

    @app.route('/questions', methods=['GET', 'POST'])
    def get_all_questions():
        if request.method == 'GET':
            try:

                page = request.args.get('page', default=1, type=int)
                questions = Question.query.all()
                formatted_questions = [q.format() for q in questions]

                if len(formatted_questions) == 0:
                    abort(404)

                categories = Category.query.all()

                formatted_categories ={categories[i].id: categories[i].type for i in range(0, len(categories), 1)}
                start = (page-1) * 10
                end = page * 10

                if len(formatted_categories) == 0:
                    abort(404)

                return jsonify({
                    'success': True,
                    'questions': formatted_questions[start:end],
                    'total_questions': len(formatted_questions),
                    'categories': formatted_categories,
                    'current_category': 1
                })
            except:
                abort(400)
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
                abort(422)
            finally:
                db.session.close()

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            Question.query.filter_by(id=question_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
        return jsonify({'success': True})

    @app.route('/questions-search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body['searchTerm']
            search = "%{}%".format(search_term.lower())
            questions = Question.query \
                .filter(db.func.lower(Question.question).like(search)).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0:
                abort(404)

            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': 1
            })

        except:
            abort(400)

    @app.route('/categories/<int:cat_id>/questions')
    def get_questions_by_cat_id(cat_id):
        try:
            questions = Question.query.filter_by(category=cat_id).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0:
                abort(404)

            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': cat_id
            })
        except:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            category = body['quiz_category']
            previous_questions = body['previous_questions']
            res_boy = get_random_question(int(category['id']), previous_questions)
            previous_questions.append(res_boy['question']['id'])
            return jsonify(res_boy)
        except:
            abort(422)

    def get_random_question(cat_id, prev_questions):
        if cat_id > 0:
            questions = Question.query.order_by('id') \
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
            'forceEnd': no_of_questions == len(prev_questions) + 1
        }

    @app.errorhandler(400)
    def bad_request():
        return jsonify({
            "success": False,
            "message": 'Bad request',
            "error": 400,
        }), 400

    @app.errorhandler(404)
    def not_found():
        return jsonify({
            "success": False,
            "message": 'Resources not found ',
            "error": 404,
        }), 404

    @app.errorhandler(422)
    def unprocessable():
        return jsonify({
            "success": False,
            "message": 'Unprocessable entity',
            "error": 404,
        }), 404

    return app
