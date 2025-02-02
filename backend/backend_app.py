from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dummy data (hardcoded blog posts)
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Flask Tutorial", "content": "Learn Flask step by step."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all posts with optional sorting based on title or content.

    Query Parameters:
        sort (str): Field to sort by ('title' or 'content').
        direction (str): Sort direction ('asc' for ascending, 'desc' for descending). Defaults to 'asc'.

    Returns:
        Response: JSON list of posts, possibly sorted, or error message if invalid parameters are given.
    """
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validate sorting parameters
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": f"Invalid sort field: {sort_field}. Must be 'title' or 'content'."}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": f"Invalid sort direction: {sort_direction}. Must be 'asc' or 'desc'."}), 400

    # Copy the original list of posts
    sorted_posts = POSTS.copy()

    # Apply sorting if parameters are specified
    if sort_field:
        reverse = (sort_direction == 'desc')
        sorted_posts.sort(key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new post to the list.

    Request Body:
        JSON containing 'title' and 'content' fields.

    Returns:
        Response: The newly created post or an error message if required fields are missing.
    """
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = [field for field in ['title', 'content'] if field not in data]
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a post by its ID.

    Parameters:
        post_id (int): ID of the post to be deleted.

    Returns:
        Response: Success message or error if the post does not exist.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_delete:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a post by its ID.

    Parameters:
        post_id (int): ID of the post to be updated.

    Request Body:
        JSON containing optional 'title' and 'content' fields.

    Returns:
        Response: Updated post or error message if the post does not exist.
    """
    global POSTS
    post_to_update = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_update:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid input"}), 400

    # Update fields only if present in the JSON body
    post_to_update["title"] = data.get("title", post_to_update["title"])
    post_to_update["content"] = data.get("content", post_to_update["content"])

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for posts by title and/or content.

    Query Parameters:
        title (str): Title query (case-insensitive substring match).
        content (str): Content query (case-insensitive substring match).

    Returns:
        Response: List of posts matching the search criteria.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    filtered_posts = [
        post for post in POSTS
        if (title_query in post['title'].lower() or not title_query) and
           (content_query in post['content'].lower() or not content_query)
    ]

    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
