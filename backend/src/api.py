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


# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    selection = Drink.query.all()
    drinks = []

    for drink in selection:
        drinks.append(drink.short())

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    selection = Drink.query.all()

    drinks = []

    for drink in selection:
        drinks.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    res = request.get_json()

    print(res)

    drinks = []

    drink = Drink(
        title=res['title'],
        recipe=json.dumps(res['recipe'])

    )
    drink.insert()

    drinks.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):

    selection = Drink.query.get(id)
    res = request.get_json()

    if not selection:
        abort(404)

    try:
        selection.title = res['title']

        if 'recipe' in res:
            selection.recipe = json.dumps(res['recipe'])

        selection.update()

    except Exception as e:
        abort(401)
        print('Exception :', e)

    return jsonify({
        "success": True,
        "drinks": [selection.long()]
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    selection = Drink.query.get(id)

    if not selection:
        abort(404)
        id = 404
    try:
        selection.delete()
    except Exception as e:
        abort(500)
        print('Exception :', e)

    return jsonify({
        "success": True,
        "delete": id
    })

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable."
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "The server can not find the requested resource."
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "You are no authorized."
    }), 401
