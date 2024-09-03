import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from openai import OpenAI
from search import rag_answer

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
# Access environment variables
openai_key = os.getenv('OPENAI_API_KEY')

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")
index_name="products"


openai_client = OpenAI()

# Route for the main chat page
@app.route('/', methods=['GET', 'POST'])
def chat():
    return render_template('chat.html')

# Route to handle chat messages
@app.route('/get_answer', methods=['POST'])
def get_answer():
    user_query = request.json.get('query')
    answer = rag_answer(user_query, es, index_name, openai_client)
    return jsonify({"query": user_query, "answer": answer})

# Route to handle feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    feedback_type = data.get('feedback')
    query = data.get('query')
    answer = data.get('answer')

    # Process the feedback (e.g., save it to a database, log it, etc.)
    print(f"Feedback: {feedback_type} for Query: '{query}' | Answer: '{answer}'")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
