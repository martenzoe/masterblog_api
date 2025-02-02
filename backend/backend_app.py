from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Aktiviert CORS für alle Routen

# Dummy-Daten (erweiterte Blog-Posts)
POSTS = [
    {
        "id": 1,
        "title": "First Post",
        "content": "This is the first post.",
        "author": "John Doe",
        "date": "2023-06-07"
    },
    {
        "id": 2,
        "title": "Second Post",
        "content": "This is the second post.",
        "author": "Jane Smith",
        "date": "2023-06-08"
    }
]


# Route: Alle Posts abrufen (GET) mit Sortierfunktion
@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    if sort_field and sort_field not in ['title', 'content', 'author', 'date']:
        return jsonify(
            {"error": f"Invalid sort field: {sort_field}. Must be 'title', 'content', 'author' or 'date'."}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": f"Invalid sort direction: {sort_direction}. Must be 'asc' or 'desc'."}), 400

    sorted_posts = POSTS.copy()
    if sort_field:
        reverse = (sort_direction == 'desc')
        if sort_field == 'date':
            sorted_posts.sort(key=lambda post: datetime.strptime(post['date'], '%Y-%m-%d'), reverse=reverse)
        else:
            sorted_posts.sort(key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


# Route: Neuen Post hinzufügen (POST)
@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    missing_fields = [field for field in ['title', 'content', 'author', 'date'] if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        datetime.strptime(data['date'], '%Y-%m-%d')  # Validierung des Datumsformats
    except ValueError:
        return jsonify({"error": f"Invalid date format: {data['date']}. Must be YYYY-MM-DD."}), 400

    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content'],
        "author": data['author'],
        "date": data['date']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


# Route: Einen Post löschen (DELETE)
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_delete:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


# Route: Einen Post aktualisieren (PUT)
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    global POSTS
    post_to_update = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_update:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()

    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')  # Validierung des Datumsformats
        except ValueError:
            return jsonify({"error": f"Invalid date format: {data['date']}. Must be YYYY-MM-DD."}), 400

    for field in ['title', 'content', 'author', 'date']:
        if field in data:
            post_to_update[field] = data[field]

    return jsonify(post_to_update), 200


# Route: Posts suchen (GET)
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    query = request.args.get('query', '').lower()

    filtered_posts = [
        post for post in POSTS
        if query in post['title'].lower() or
           query in post['content'].lower() or
           query in post['author'].lower() or
           query in post['date']
    ]

    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
