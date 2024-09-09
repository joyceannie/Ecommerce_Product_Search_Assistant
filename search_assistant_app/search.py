from elasticsearch import Elasticsearch

PROMPT_TEMPLATE = """
You're the product search assistant for an ecommerce website. Answer the QUESTION based on the CONTEXT from our products database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

ENTRY_TEMPLATE = """
title: {title}
description: {description}
category: {category}
sub_category: {sub_category}
brand: {brand}
average rating: {average_rating}
url: {url}
out_of_stock: {out_of_stock}
""".strip()   

def full_text_search(query, es, index_name):
    response = es.search(
        index=index_name,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description"]
                }
            }
        }
    )
    for result in response['hits']['hits']:
        return [result]

def build_prompt(query, search_results, context):
    if search_results:
        for doc in search_results:
            context = context + ENTRY_TEMPLATE.format(**doc['_source']) + "\n\n"

    prompt = PROMPT_TEMPLATE.format(question=query, context=context).strip()
    return prompt

    
def llm(prompt, openai_client):
    model='gpt-4o-mini'
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag_answer(query, es, index_name, openai_client, context):
    search_results = full_text_search(query, es, index_name)
    prompt = build_prompt(query, search_results, context)
    answer = llm(prompt, openai_client)
    return answer

