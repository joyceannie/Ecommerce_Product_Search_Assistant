import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from elasticsearch import Elasticsearch
from openai import OpenAI
from search import rag_answer
from uuid import uuid4
import db

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key') 

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()
# Access environment variables
openai_key = os.getenv('OPENAI_API_KEY')

ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
es = Elasticsearch([ES_HOST])
index_name = os.getenv('INDEX_NAME')


# Optional: Test the connection
try:
    if es.ping():
        print("Successfully connected to Elasticsearch")
    else:
        print("Could not connect to Elasticsearch")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {e}")


openai_client = OpenAI()

# Route for rendering the main chatbot page
@app.route('/')
def home():
    # Generate a unique session ID if not already set
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())
        session['conversation_count'] = 0
        session['context'] = ''
    return render_template('index.html')

# Route to handle the search query and return results
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    session_id = session.get('session_id')
    context = session.get('context', '') or ''
    session['conversation_count'] = session.get('conversation_count', 0)  + 1
    conversation_id = f"{session_id}_{session.get('conversation_count')}"
    results = rag_answer(query, es, index_name, openai_client, context)
    session['context'] = context + results
    if len(session.get('context')) > 5000: 
        session['context'] =session.get('context')[1000:]
    db.save_conversation(
    conversation_id=conversation_id,
    question=query,
    answer_data=results,
    )
    return render_template('results.html', results=results)

# Route to handle feedback submission
@app.route('/feedback', methods=['POST'])
def feedback():
    # result_id = request.form.get('result_id')
    conversation_id = request.form.get('conversation_id')
    feedback_type = request.form.get('feedback_type')
    feedback = 1 if feedback_type == 'like' else -1
    conversation_id = f"{session['session_id']}_{session['conversation_count']}"
    print(f"Received feedback: {feedback_type} for {conversation_id}")
    db.save_feedback(conversation_id=conversation_id, feedback=feedback)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
