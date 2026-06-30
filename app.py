from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

# Ensure your folder structure is:
# /project_folder
#   /templates
#     index.html
#   app.py

app = Flask(__name__, template_folder='templates')
CORS(app)

# Fetch the API key from environment variables
API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Hardcoded list of allowed IP addresses for your instance on Render
AUTHORIZED_IPS = ["80.225.202.209", "127.0.0.1"]

def is_authorized(request):
    """Check if the client IP is in the authorized list."""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    return client_ip in AUTHORIZED_IPS

# NEW: Route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/video', methods=['GET'])
def get_metadata():
    # 1. Authorize the request
    if not is_authorized(request):
        return jsonify({"error": {"message": "Unauthorized IP access"}}), 403

    # 2. Check for API key configuration
    if not API_KEY:
        return jsonify({"error": {"message": "API Key not configured on server"}}), 500

    # 3. Get Video ID directly from the request arguments
    video_id = request.args.get('id')
    
    if not video_id:
        return jsonify({"error": {"message": "Video ID missing"}}), 400

    # 4. Fetch data from YouTube API
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={API_KEY}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        # 5. Return appropriate JSON structure for the frontend
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
