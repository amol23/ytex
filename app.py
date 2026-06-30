from flask import Flask, request, jsonify, render_template, abort
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

ALLOWED_IP = '80.225.202.209'

def restrict_ip(f):
    def wrapper(*args, **kwargs):
        # Render and other proxies put the real client IP in X-Forwarded-For
        # The header can be a comma-separated list; the first one is the client.
        forwarded_for = request.headers.get('X-Forwarded-For')
        client_ip = forwarded_for.split(',')[0] if forwarded_for else request.remote_addr
        
        if client_ip != ALLOWED_IP:
            # 403 Forbidden
            abort(403)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
@restrict_ip
def index():
    return render_template('index.html')

@app.route('/api/video')
@restrict_ip
def get_video_metadata():
    video_id = request.args.get('id')
    api_key = os.environ.get('YOUTUBE_API_KEY')

    if not api_key:
        return jsonify({"error": "Missing API Key"}), 500

    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=3000)
