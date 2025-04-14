from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOUR_API_URL = 'https://core2.easetravelandtours.com/api/fetch-tour'

@app.route('/')
def index():
    return jsonify({"message": "Tour recommender API is running."})

@app.route('/recommend-tours', methods=['POST'])
def recommend():
    try:
        user_data = request.json
        budget = float(user_data.get('budget', 999999))
        selected_types = [t.lower() for t in user_data.get('tour_type', [])]

        api_response = requests.get(TOUR_API_URL)
        if not api_response.ok:
            return jsonify({"error": "Failed to fetch tours"}), 500

        all_tours = api_response.json().get('data', [])
        recommended = []

        for tour in all_tours:
            if tour.get('availability', '').lower() != 'available':
                continue

            tour_type = tour.get('tour_type', '').lower()
            if selected_types and tour_type not in selected_types:
                continue

            price = float(tour.get('price', 0))
            if price > budget:
                continue

            # Optional: Add score (e.g., for discounts)
            score = 0
            if tour.get('discounts'):
                score += 1

            tour['score'] = score
            recommended.append(tour)

        recommended.sort(key=lambda x: x['score'], reverse=True)

        return jsonify({
            "recommendations": recommended,
            "count": len(recommended)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
