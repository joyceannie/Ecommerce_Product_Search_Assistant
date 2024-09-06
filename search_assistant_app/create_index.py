from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from sentence_transformers import SentenceTransformer
import logging
import time


logging.basicConfig(level=logging.INFO)

def initialize_elasticsearch():
    # Initialize Elasticsearch client
    es = Elasticsearch("http://elasticsearch:9200")
    if not es.ping():
        raise ValueError("Connection to Elasticsearch failed")
    return es

def create_index(es):
    # Define index settings and mappings
    index_name = 'products_index'
    if es.indices.exists(index=index_name):
        return index_name

    es.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "category": {"type": "keyword"},
                    "sub_category": {"type": "keyword"},
                    "brand": {"type": "keyword"},
                    "product_details": {
                        "type": "nested",
                        "dynamic": "true"
                    },
                    "average_rating": {"type": "float"},
                    "url": {"type": "text"},
                    "out_of_stock": {"type": "boolean"},
                    "title_and_description_vector": {"type": "dense_vector", "dims": 768, "index": True, "similarity": "cosine"},
                }
            }
        }
    )
    return index_name

def wait_for_elasticsearch(es, max_attempts=30, delay=10):
    for attempt in range(max_attempts):
        try:
            if es.ping():
                health = es.cluster.health()
                if health['status'] == 'green':
                    return True
        except ConnectionError as e:
            print(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
        time.sleep(delay)
    raise RuntimeError("Elasticsearch did not become available")

def load_model():
    model = SentenceTransformer("all-mpnet-base-v2")
    return model

def index_documents(file_name, index_name, es_client, model):
    index = 0
    documents = []
    
    try:
        with open(file_name, "r") as json_file:
            json_data = json.load(json_file)
            for doc in json_data:
                new_doc = {
                    "title": doc.get('title', ''),
                    "description": doc.get('description', ''),
                    "category": doc.get('category', ''),
                    "sub_category": doc.get('sub_category', ''),
                    "brand": doc.get('brand', ''),
                    'doc_id': index,
                    'product_details': doc.get('product_details', [{}])[0],
                    'average_rating': doc.get('average_rating', 0.0),
                    'url': doc.get('url', ''),
                    'out_of_stock': doc.get('out_of_stock', False),
                    "title_and_description_vector": model.encode(
                        f"{doc.get('title', '')} {doc.get('description', '')}"
                    ).tolist()
                }
                
                documents.append(new_doc)
                index += 1

                logging.info(f'Processed {index} documents')
                
                if index == 100:
                    break

        # Use bulk indexing for better performance
        bulk(es_client, documents, index=index_name)
    except Exception as e:
        logging.error(f"Error indexing documents: {e}")

def main():
    try:
        es_client = initialize_elasticsearch()
        wait_for_elasticsearch(es_client)
        index_name = create_index(es_client)
        model = load_model()
        file_name = 'data/cleaned_data.json'
        index_documents(file_name, index_name, es_client, model)
        logging.info('Indexed documents')
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()