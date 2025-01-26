from flask import Flask, request, jsonify
from openai import OpenAI
import prompts
import ignore
from pydantic import BaseModel, Field
from typing import List, Optional
import json
from flask_cors import CORS
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5173", "http://localhost:5173"],  # Allow both localhost and IP
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

class RTData(BaseModel):
    rt_link: str = Field(description="Link to the movie on Rotten Tomatoes")
    poster_url: str = Field(description="URL of the movie poster")
    tomato_score: str = Field(description="Rotten Tomatoes score")

class TitleItem(BaseModel):
    title: str = Field(description="The title of a search result")
    description: str = Field(description="A brief description of the search result")
    confidence: float = Field(description="Confidence score for this result", ge=0, le=1)
    rt_data: Optional[RTData] = Field(description="Rotten Tomatoes data for the movie", default=None)

class SearchResponse(BaseModel):
    results: List[TitleItem] = Field(description="List of search results")
    query_understood: bool = Field(description="Whether the search query was properly understood")
    total_results: int = Field(description="Total number of results found")

def get_rt_data(movie_title: str) -> Optional[RTData]:
    try:
        # Construct search URL
        search_url = f"https://www.rottentomatoes.com/search?search={quote(movie_title)}"
        print(search_url)
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(search_url, headers=headers)
        if not response.ok:
            return None
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First find the movie results section
        movie_section = soup.find('search-page-result', attrs={'type': 'movie'})
        if not movie_section:
            print("No movie section found for", movie_title)
            return None
            
        # Find all movie rows within the section
        movie_rows = movie_section.find_all('search-page-media-row')
        if not movie_rows:
            print("No movie results found for", movie_title)
            return None
            
        # Find the matching movie by comparing titles
        for row in movie_rows:
            title_element = row.find('a', {'data-qa': 'info-name'})
            if not title_element:
                continue
                
            if title_element.text.strip().lower() == movie_title.lower():
                # Found exact match
                rt_link = title_element['href']
                if not rt_link.startswith('https://www.rottentomatoes.com'):
                    rt_link = 'https://www.rottentomatoes.com' + rt_link
                    
                poster_img = row.find('img')
                poster_url = poster_img['src'] if poster_img else ''
                
                # Get tomato score from the row's attributes
                tomato_score = row.get('tomatometerscore', 'N/A')
                
                return RTData(
                    rt_link=rt_link,
                    poster_url=poster_url,
                    tomato_score=tomato_score
                )
        
        # If no exact match found, use the first result
        first_row = movie_rows[0]
        first_link = first_row.find('a', {'data-qa': 'info-name'})
        rt_link = first_link['href']
        if not rt_link.startswith('https://www.rottentomatoes.com'):
            rt_link = 'https://www.rottentomatoes.com' + rt_link
            
        poster_img = first_row.find('img')
        poster_url = poster_img['src'] if poster_img else ''
        
        tomato_score = first_row.get('tomatometerscore', 'N/A')
        
        return RTData(
            rt_link=rt_link,
            poster_url=poster_url,
            tomato_score=tomato_score
        )
            
    except Exception as e:
        print(f"Error fetching RT data for {movie_title}: {str(e)}")
        return None

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    # Do not remove this code. it will be used after testing is done
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
    
    # Simulate LLM response for now
    time.sleep(2)
    
    # Get initial movie results
    initial_results = {
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
    }
    
    # Enhance results with Rotten Tomatoes data
    enhanced_results = []
    for movie in initial_results["results"]:
        rt_data = get_rt_data(movie["title"])
        enhanced_results.append(TitleItem(
            title=movie["title"],
            description=movie["description"],
            confidence=movie["confidence"],
            rt_data=rt_data
        ))
    
    response = SearchResponse(
        results=enhanced_results,
        query_understood=initial_results["query_understood"],
        total_results=initial_results["total_results"]
    )
    
    return jsonify(response.model_dump())

if __name__ == '__main__':
    app.run(debug=True)
