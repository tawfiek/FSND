import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES

'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks',  methods=['GET'])
@requires_auth()
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        print('Drinks => ', len(drinks))

        formatted_drinks = [drink.short() for drink in drinks]

        if len(formatted_drinks) == 0:
            abort(404)

        res = {"success": True, "drinks": formatted_drinks}
        return jsonify(res)

    except:
        abort(400)


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail',  methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_all_drinks_details():
    try:
        drinks = Drink.query.all()
        print('Drinks => ', len(drinks))

        formatted_drinks = [drink.long() for drink in drinks]

        if len(formatted_drinks) == 0:
            abort(404)

        res = {"success": True, "drinks": formatted_drinks}
        return jsonify(res)

    except:
        abort(400)


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks',  methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink():
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title is None:
            abort(400)
        if recipe is None:
            abort(400)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({"success": True, "drinks": drink.long()})
    except:
        abort(400)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(id):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink.query.filter_by(id=id).one_or_none()

        if drink is None:
            abort(404)
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except:
        pass
        abort(400)


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({"success": True, "delete": id})
    except:
        abort(400)

## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "message": 'Bad request',
        "error": 400,
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": 'Resources not found ',
        "error": 404,
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "message": 'Unprocessable entity',
        "error": 422,
    }), 422


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "message": 'Unexpected Error',
        "error": 500,
    }), 500


@app.errorhandler(AuthError)
def auth_error_handler(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
        }), error.status_code
