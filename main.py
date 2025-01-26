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
    release_year: Optional[str] = Field(description="Release year of the movie", default=None)
    cast: Optional[str] = Field(description="List of main cast members", default=None)

class TitleItem(BaseModel):
    title: str = Field(description="The title of a search result")
    description: str = Field(description="A brief description of the search result")
    confidence: float = Field(description="Confidence score for this result", ge=0, le=1)
    rt_data: Optional[RTData] = Field(description="Rotten Tomatoes data for the movie", default=None)

class SearchResponse(BaseModel):
    results: List[TitleItem] = Field(description="List of search results")
    query_understood: bool = Field(description="Whether the search query was properly understood")
    total_results: int = Field(description="Total number of results found")
    bad_query: bool = Field(description="Whether the query was not related to movies", default=False)

def get_rt_data(movie_title: str) -> Optional[RTData]:
    try:
        # Construct search URL
        search_url = f"https://www.rottentomatoes.com/search?search={quote(movie_title)}"
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
                
            # Extract year from the row's attributes
            release_year = row.get('releaseyear', '')
            if not release_year:
                # Try to find year in the row's content
                year_span = row.find('span', {'data-qa': 'release-year'})
                if year_span:
                    release_year = year_span.text.strip('()')
                    
            # Extract cast from the row's attributes
            cast = row.get('cast', '')
                
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
                    tomato_score=tomato_score,
                    release_year=release_year,
                    cast=cast
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
        
        # Extract year from the first result
        release_year = first_row.get('releaseyear', '')
        if not release_year:
            year_span = first_row.find('span', {'data-qa': 'release-year'})
            if year_span:
                release_year = year_span.text.strip('()')
                
        # Extract cast from the first result
        cast = first_row.get('cast', '')
        
        return RTData(
            rt_link=rt_link,
            poster_url=poster_url,
            tomato_score=tomato_score,
            release_year=release_year,
            cast=cast
        )
            
    except Exception as e:
        print(f"Error fetching RT data for {movie_title}: {str(e)}")
        return None

def get_llm_response(query: str) -> Optional[SearchResponse]:
    try:
        headers = {
            "Authorization": f"Bearer {ignore.API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": prompts.assistant_prompt
                },
                {"role": "user", "content": query}
            ],
            "response_format": {"type": "json_object"},
            "stream": False
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}: {response.text}")
            return None
            
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        parsed_data = json.loads(content)
        return SearchResponse(**parsed_data)
        
    except Exception as e:
        print(f"Error getting LLM response: {str(e)}")
        return None

def enhance_with_rt_data(results: List[TitleItem]) -> List[TitleItem]:
    enhanced_results = []
    for movie in results:
        rt_data = get_rt_data(movie.title)
        # Add release year to title if available
        title_with_year = movie.title
        if rt_data and rt_data.release_year:
            title_with_year = f"{movie.title}"
            
        enhanced_results.append(TitleItem(
            title=title_with_year,
            description=movie.description,
            confidence=movie.confidence,
            rt_data=rt_data
        ))
    return enhanced_results

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    initial_results = get_llm_response(query)
    if not initial_results:
        return jsonify({'error': 'Failed to process response'}), 500
    
    if initial_results.bad_query:
        return jsonify(initial_results.model_dump())
    
    enhanced_results = enhance_with_rt_data(initial_results.results)
    
    response = SearchResponse(
        results=enhanced_results,
        query_understood=initial_results.query_understood,
        total_results=initial_results.total_results,
        bad_query=initial_results.bad_query
    )
    
    return jsonify(response.model_dump())

if __name__ == '__main__':
    app.run(debug=True)
