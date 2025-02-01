from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Aktiviert CORS für alle Routen

# Dummy-Daten (harcodierte Blog-Posts)
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
]

# Route: Alle Posts abrufen (GET)
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

# Route: Neuen Post hinzufügen (POST)
@app.route('/api/posts', methods=['POST'])
def add_post():
    # JSON-Daten aus der Anfrage abrufen
    data = request.get_json()

    # Validierung: Prüfen, ob 'title' und 'content' vorhanden sind
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = []
        if 'title' not in data:
            missing_fields.append('title')
        if 'content' not in data:
            missing_fields.append('content')
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Neue ID generieren (höchste bestehende ID + 1)
    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    # Neuen Post erstellen
    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    # Post zur Liste hinzufügen
    POSTS.append(new_post)

    # Erfolgsantwort zurückgeben
    return jsonify(new_post), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
