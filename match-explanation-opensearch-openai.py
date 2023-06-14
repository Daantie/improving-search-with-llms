from opensearchpy import OpenSearch, RequestsHttpConnection
from decouple import config
import openai
import json

openai.api_key = config('OPENAI-KEY')
opensearch_host = config('OS-HOST')
# Using basic auth with OpenSearch here
auth = (config('OS-USER'), config('OS-PASSWORD'))


def query():
    opensearch = OpenSearch(hosts=[opensearch_host], http_auth=auth)
    query_string = "Machine Learning"

    body = {
        "query": {
            "multi_match": {
                "query": query_string,
                "fields": ["title", "content"]
            }
        }
    }

    try:
        response = opensearch.search(index="blogs", body=body)
        # Initial search results
        initial_results = response['hits']['hits']
        explained_results = []

        for result in initial_results:
            # Instructions for the LLM
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that explains why a search result matches a given query in three sentences.",
                },
                {
                    "role": "system",
                    "content": "You start every explanation with \"This result matches the query because\".",
                },
                {
                    "role": "user",
                    "content": f"query: {query_string}, result: {result['_source']}"
                }
            ]

            # Generate an explanation for the document
            match_explanation = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.5,
                max_tokens=100
            )

            # Combine title and explanation
            explained_results.append({
                "title": result['_source']['title'],
                "match_explanation": match_explanation["choices"][0]['message']['content']
            })

        print(json.dumps(explained_results, indent=4))
    except Exception as e:
        print('Error')
        print(str(e))


query()
