from flask import Flask, request, jsonify
from openai import OpenAI
import prompts
import ignore
from pydantic import BaseModel, Field
from typing import List
import json

app = Flask(__name__)

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
    
    client = OpenAI(api_key=ignore.API_KEY, base_url="https://api.deepseek.com")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": prompts.assistant_prompt
                },
                {"role": "user", "content": query},
            ],
            response_format={"type": "json_object"},
            stream=False
        )
        
        # Parse and validate the response using Pydantic
        response_data = json.loads(response.choices[0].message.content)
        structured_response = SearchResponse(**response_data)
        
        return jsonify(structured_response.model_dump())
        
    except Exception as e:
        return jsonify({'error': 'Failed to process response', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
