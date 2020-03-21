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


#db_drop_and_create_all()

## ROUTES

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

    drinks=[]

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

    drinks = []

    drink = Drink(
        title= res.get('title'), 
        recipe= json.dumps(res['recipe'])

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
    selection = Drink.query.get(id).one_or_none()
    res = request.get_json()

    if not selection:
        abort(404)

    drinks = []

    try:
        drink = Drink(
            id = res.get('id', None),
            title = res.get('title', None),
            recipe = res.get('recipe', None ) 
        )

        drink.update()
        drinks.append(drink.long())
    except:
        abort(500)

    return jsonify({
        "success": True, 
        "drinks": drinks
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
    except:
        abort(500)

    return jsonify({
        "success": True, 
        "delete": id
    })

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable. The request was well-formed but was unable to be followed due to semantic errors."
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return({
        "success": False, 
        "error": 404,
        "message": "The server can not find the requested resource."
    }),404

@app.errorhandler(401)
def auth_error(error):
    return({
        "success": False, 
        "error": 401,
        "message": "You have no authorized. the client must authenticate itself to get the requested response"
    }),401