import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from elasticsearch import Elasticsearch
from openai import OpenAI
from search import rag_answer
from uuid import uuid4
from db import save_conversation, save_feedback

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key') 

logging.basicConfig(level=logging.INFO)


# Load environment variables from .env file
load_dotenv()
# Access environment variables
openai_key = os.getenv('OPENAI_API_KEY')

# es_host = os.getenv('ELASTIC_URL_LOCAL')
es_host = os.getenv('ELASTIC_HOST')
es_port = int(os.getenv('ELASTIC_PORT'))
index_name = os.getenv('INDEX_NAME')

# Initialize Elasticsearch client
es = Elasticsearch(
    hosts=[{
        'host': es_host,
        'port': es_port,
        'scheme': 'http'
    }]
)
# es  = Elasticsearch(hosts=[{'host': 'localhost', 'scheme': 'http', 'port': 9200}])

# Optional: Test the connection
try:
    if es.ping():
        print("Successfully connected to Elasticsearch")
    else:
        print("Could not connect to Elasticsearch")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {e}")


openai_client = OpenAI()

# Route for the main chat page
@app.route('/', methods=['GET', 'POST'])
def chat():
    # Generate a unique session ID if not already set
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())
        session['conversation_count'] = 0
    return render_template('chat.html')

# Route to handle chat messages
@app.route('/get_answer', methods=['POST'])
def get_answer():
    user_query = request.json.get('query')
    session_id = session['session_id']
    session['conversation_count'] += 1
    conversation_id = f"{session_id}_{session['conversation_count']}"
    answer = rag_answer(user_query, es, index_name, openai_client)
    # Save the conversation to the database
    timestamp = datetime.now()
    # save_conversation(conversation_id, user_query, answer, timestamp)
    return jsonify({"query": user_query, "answer": answer})

# Route to handle feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    feedback_type = data.get('feedback')
    query = data.get('query')
    answer = data.get('answer')
    
    conversation_id = f"{session['session_id']}_{session['conversation_count']}"
    timestamp = datetime.now()
    # Process the feedback (e.g., save it to a database, log it, etc.)
    # save_feedback(conversation_id, feedback_type, timestamp)

    return jsonify({"status": "success"})
