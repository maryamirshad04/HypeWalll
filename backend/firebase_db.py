# firebase_db.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Build credentials dictionary from environment variables
cred_dict = {
    "type": os.environ["FIREBASE_TYPE"],
    "project_id": os.environ["FIREBASE_PROJECT_ID"],
    "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
    "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
    "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
    "client_id": os.environ["FIREBASE_CLIENT_ID"],
    "auth_uri": os.environ["FIREBASE_AUTH_URI"],
    "token_uri": os.environ["FIREBASE_TOKEN_URI"],
    "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_CERT_URL"],
    "client_x509_cert_url": os.environ["FIREBASE_CLIENT_CERT_URL"]
}

# Initialize Firebase
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------- BOARDS ----------

def create_board(board_data):
    db.collection("boards").document(board_data["id"]).set(board_data)

def get_board(board_id):
    doc = db.collection("boards").document(board_id).get()
    return doc.to_dict() if doc.exists else None

def get_board_by_join_code(code):
    boards = db.collection("boards").where("join_code", "==", code).limit(1).stream()
    for board in boards:
        return board.to_dict()
    return None

def get_board_by_view_token(token):
    boards = db.collection("boards").where("view_token", "==", token).limit(1).stream()
    for board in boards:
        return board.to_dict()
    return None

# ---------- COMMENTS ----------

def add_comment(board_id, comment):
    db.collection("boards").document(board_id) \
      .collection("comments").document(comment["id"]).set(comment)

def get_comments(board_id):
    comments_ref = db.collection("boards").document(board_id).collection("comments")
    return [doc.to_dict() for doc in comments_ref.order_by("created_at").stream()]
