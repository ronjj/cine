from flask import Flask, request, jsonify
from openai import OpenAI
import ignore  

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    client = OpenAI(api_key=ignore.API_KEY, base_url="https://api.deepseek.com")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": query},
        ],
        stream=False
    )
    
    return jsonify({'results': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)
