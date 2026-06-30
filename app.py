from flask import Flask, request, jsonify, render_template
import requests
import os

# Updated to correctly include the template_folder parameter
app = Flask(__name__, static_folder='static', template_folder='templates')

# Serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/video')
def get_video_metadata():
    video_id = request.args.get('id')
    api_key = os.environ.get('YOUTUBE_API_KEY')
    
    if not api_key:
        return jsonify({"error": "Missing API Key"}), 500
        
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=3000)
