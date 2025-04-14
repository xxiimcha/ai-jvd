from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOUR_API_URL = 'https://core2.easetravelandtours.com/api/fetch-tour'

# Map keywords in interests to likely match descriptions
TAG_MAP = {
    "adventure": ["adventure", "island", "hopping", "snorkel", "kayak"],
    "relaxation": ["relax", "beach", "spa", "resort"],
    "culture": ["historical", "culture", "heritage", "museum", "church"],
    "food": ["food", "culinary", "local dish", "restaurant"]
}

@app.route('/')
def index():
    return jsonify({"message": "Tour recommender API is running."})

@app.route('/recommend-tours', methods=['POST'])
def recommend():
    try:
        user_data = request.json
        interests = [i.lower() for i in user_data.get('interests', [])]
        budget = float(user_data.get('budget', 999999))

        api_response = requests.get(TOUR_API_URL)
        if not api_response.ok:
            return jsonify({"error": "Failed to fetch tours"}), 500

        all_tours = api_response.json().get('data', [])
        recommended = []

        for tour in all_tours:
            if tour['availability'].lower() != 'available':
                continue

            price = float(tour.get('price', 0))
            if price > budget:
                continue

            score = 0
            description = f"{tour.get('location', '')} {tour.get('packages', '')}".lower()

            for interest in interests:
                keywords = TAG_MAP.get(interest, [interest])
                if any(keyword in description for keyword in keywords):
                    score += 1

            if score > 0:
                tour['score'] = score
                recommended.append(tour)

        recommended.sort(key=lambda x: x['score'], reverse=True)

        return jsonify({"recommendations": recommended, "count": len(recommended)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
