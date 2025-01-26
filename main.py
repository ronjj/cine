from flask import Flask, request, jsonify
from openai import OpenAI
import prompts
import ignore
from pydantic import BaseModel, Field
from typing import List
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5173", "http://localhost:5173"],  # Allow both localhost and IP
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Define Pydantic model for structured output
class TitleItem(BaseModel):
    title: str = Field(description="The title of a search result")
    description: str = Field(description="A brief description of the search result")
    confidence: float = Field(description="Confidence score for this result", ge=0, le=1)

class SearchResponse(BaseModel):
    results: List[TitleItem] = Field(description="List of search results")
    query_understood: bool = Field(description="Whether the search query was properly understood")
    total_results: int = Field(description="Total number of results found")

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    # client = OpenAI(api_key=ignore.API_KEY, base_url="https://api.deepseek.com")
    
    # try:
    #     response = client.chat.completions.create(
    #         model="deepseek-chat",
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": prompts.assistant_prompt
    #             },
    #             {"role": "user", "content": query},
    #         ],
    #         response_format={"type": "json_object"},
    #         stream=False
    #     )
        
    #     # Parse and validate the response using Pydantic
    #     response_data = json.loads(response.choices[0].message.content)
    #     structured_response = SearchResponse(**response_data)
        
    #     return jsonify(structured_response.model_dump())

    # except Exception as e:
    #     return jsonify({'error': 'Failed to process response', 'details': str(e)}), 500

    return jsonify({
    "query_understood": True,
    "results": [
        {
            "confidence": 0.9,
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "title": "The Matrix"
        },
        {
            "confidence": 0.88,
            "description": "A wealthy New York City investment banking executive, Patrick Bateman, hides his alternate psychopathic ego from his co-workers and friends as he delves deeper into his violent, hedonistic fantasies.",
            "title": "American Psycho"
        },
        {
            "confidence": 0.85,
            "description": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.",
            "title": "Se7en"
        },
        {
            "confidence": 0.87,
            "description": "A troubled teenager is plagued by visions of a man in a large rabbit suit who manipulates him to commit a series of crimes, after he narrowly escapes a bizarre accident.",
            "title": "Donnie Darko"
        },
        {
            "confidence": 0.89,
            "description": "In a future British tyranny, a shadowy freedom fighter, known only by the alias of 'V', plots to overthrow it with the help of a young woman.",
            "title": "V for Vendetta"
        }
    ],
    "total_results": 5
})

if __name__ == '__main__':
    app.run(debug=True)
