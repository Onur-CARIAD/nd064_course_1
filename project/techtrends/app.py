import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash

# ------------------------------------------------------------------------------
# Flask application setup
# ------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# ------------------------------------------------------------------------------
# Logging configuration (STDOUT, timestamp, DEBUG level)
# ------------------------------------------------------------------------------

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s: %(message)s'
)
handler.setFormatter(formatter)

root_logger.handlers.clear()
root_logger.addHandler(handler)

# Ensure Flask propagates logs upward
app.logger.propagate = True

# ------------------------------------------------------------------------------
# Database configuration
# ------------------------------------------------------------------------------

DATABASE = "database.db"
db_connection_count = 0

def get_db_connection():
    global db_connection_count
    db_connection_count += 1
    app.logger.debug("Database connection opened")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()
    connection.close()
    return post

# ------------------------------------------------------------------------------
# Health check endpoint
# ------------------------------------------------------------------------------

@app.route('/healthz')
def status():
    app.logger.debug("Status endpoint accessed")
    return jsonify({"result": "OK - healthy"}), 200

# ------------------------------------------------------------------------------
# Metrics endpoint
# ------------------------------------------------------------------------------

@app.route('/metrics')
def metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    conn.close()

    return jsonify({
        "db_connection_count": db_connection_count,
        "post_count": post_count
    }), 200

# ------------------------------------------------------------------------------
# Main page
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# ------------------------------------------------------------------------------
# Article page
# ------------------------------------------------------------------------------

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    if post is None:
        app.logger.warning(f"Non-existing article accessed. ID: {post_id}")
        return render_template('404.html'), 404

    app.logger.info(f"Article retrieved. Title: {post['title']}")
    return render_template('post.html', post=post)

# ------------------------------------------------------------------------------
# About page
# ------------------------------------------------------------------------------

@app.route('/about')
def about():
    app.logger.info("About Us page retrieved")
    return render_template('about.html')

# ------------------------------------------------------------------------------
# Create post
# ------------------------------------------------------------------------------

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content)
            )
            connection.commit()
            connection.close()

            app.logger.info(f"New article created. Title: {title}")
            return redirect(url_for('index'))

    return render_template('create.html')

# ------------------------------------------------------------------------------
# Application startup
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=7111, debug=True)