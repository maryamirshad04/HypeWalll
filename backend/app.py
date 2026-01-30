# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import random
import string
from datetime import datetime
from dotenv import load_dotenv  # <-- added
import os

# Load environment variables from .env at the very start
load_dotenv()

from .firebase_db import (
    create_board,
    get_board as get_board_db,
    get_board_by_join_code,
    get_board_by_view_token,
    add_comment,
    get_comments
)

app = Flask(__name__)
CORS(app)


def generate_code():
    """Generate a 6-character alphanumeric code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route('/api/boards', methods=['POST'])
def create_board_api():
    data = request.json
    aesthetic = data.get('aesthetic', 'professional')
    recipient_name = data.get('recipient_name', 'Someone Special')

    board_id = str(uuid.uuid4())
    join_code = generate_code()
    view_token = str(uuid.uuid4())

    board_data = {
        'id': board_id,
        'aesthetic': aesthetic,
        'recipient_name': recipient_name,
        'join_code': join_code,
        'view_token': view_token,
        'created_at': datetime.now().isoformat(),
        'contributor_link': f'/index.html?contribute={board_id}',
        'view_link': f'/index.html?view={view_token}'
    }

    create_board(board_data)
    return jsonify(board_data), 201


@app.route('/api/boards/code/<code>', methods=['GET'])
def get_board_by_code(code):
    board = get_board_by_join_code(code.upper())
    if board:
        return jsonify({
            'id': board['id'],
            'aesthetic': board['aesthetic'],
            'recipient_name': board['recipient_name'],
            'join_code': board['join_code']
        }), 200
    return jsonify({'error': 'Board not found'}), 404


@app.route('/api/boards/<board_id>', methods=['GET'])
def get_board_api(board_id):
    board = get_board_db(board_id)
    if board:
        return jsonify(board), 200
    return jsonify({'error': 'Board not found'}), 404


@app.route('/api/boards/view/<view_token>', methods=['GET'])
def view_board(view_token):
    board = get_board_by_view_token(view_token)
    if board:
        board['comments'] = get_comments(board['id'])
        return jsonify(board), 200
    return jsonify({'error': 'Board not found'}), 404


@app.route('/api/boards/<board_id>/comments', methods=['POST'])
def add_comment_api(board_id):
    board = get_board_db(board_id)
    if not board:
        return jsonify({'error': 'Board not found'}), 404

    data = request.json
    comment = {
        'id': str(uuid.uuid4()),
        'author': data.get('author', 'Anonymous'),
        'message': data.get('message', ''),
        'color': data.get('color', '#FFD700'),
        'created_at': datetime.now().isoformat()
    }

    add_comment(board_id, comment)
    return jsonify(comment), 201


@app.route('/api/boards/<board_id>/comments', methods=['GET'])
def get_comments_api(board_id):
    board = get_board_db(board_id)
    if not board:
        return jsonify({'error': 'Board not found'}), 404

    return jsonify(get_comments(board_id)), 200

# Export for Vercel
app = app # Vercel will automatically find 'app'

if __name__ == "__main__":
    app.run(debug=True)