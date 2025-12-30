import os
from flask import Flask, request, jsonify
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

def get_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    })
    return session

def get_game_icon(session, place_id):
    try:
        thumb_url = f"https://thumbnails.roblox.com/v1/places/gameicons?placeIds={place_id}&returnPolicy=PlaceHolder&size=512x512&format=Png&isCircular=false"
        res = session.get(thumb_url, timeout=10).json()
        if res and "data" in res:
            return res["data"][0].get("imageUrl")
    except:
        pass
    return None

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/search")
def search_roblox_api():
    query = request.args.get("query")
    limit = int(request.args.get("limit", 10))
    
    if not query:
        return jsonify({"error": "query parametresi zorunlu"}), 400
    
    session = get_session()
    url = f"https://apis.roblox.com/search-api/omni-search?searchQuery={query}&sessionId=test_hhasan_123"

    try:
        response = session.get(url, timeout=20)
        data = response.json()
        results = data.get("searchResults", [])
        
        games = []
        for result in results:
            for item in result.get("contents", []):
                place_id = item.get("rootPlaceId")
                if place_id:
                    games.append({
                        "name": item.get("name"),
                        "place_id": place_id,
                        "icon": get_game_icon(session, place_id)
                    })
                if len(games) >= limit:
                    break
            if len(games) >= limit:
                break
        
        return jsonify({"games": games})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
