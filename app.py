from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Fetch the API key from environment variables
API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Hardcoded list of allowed IP addresses
AUTHORIZED_IPS = ["123.45.67.89", "98.76.54.32"]

def is_authorized(request):
    """
    Check if the client IP is in the hardcoded allowed list.
    Handles X-Forwarded-For headers which are common when hosted on platforms like Render.
    """
    # Check X-Forwarded-For if behind a proxy (like Render's load balancer)
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # If multiple IPs exist in X-Forwarded-For, the first one is the client
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
        
    return client_ip in AUTHORIZED_IPS

def extract_video_id(url):
    """
    Robustly extract YouTube video ID from various URL formats
    (Standard, Shorts, youtu.be, etc.)
    """
    reg_exp = r"(?:https?:\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|shorts\/|live\/))([a-zA-Z0-9_-]{11})"
    match = re.search(reg_exp, url)
    return match.group(1) if match else None

@app.route('/api/video', methods=['GET'])
def get_metadata():
    if not is_authorized(request):
        return jsonify({"error": {"message": "Unauthorized IP access"}}), 403

    if not API_KEY:
        return jsonify({"error": {"message": "API Key not configured on server"}}), 500

    video_id = request.args.get('id')
    
    if not video_id:
        return jsonify({"error": {"message": "Video ID missing"}}), 400

    # Ensure we are requesting both snippet and statistics
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={API_KEY}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            return jsonify({
                "items": [
                    {
                        "snippet": data['items'][0]['snippet'],
                        "statistics": data['items'][0]['statistics']
                    }
                ]
            })
        else:
            return jsonify({"error": {"message": "Video not found or is private."}}), 404
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
