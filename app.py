from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video_games.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Game(db.Model):
    image = db.Column(db.String(200), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    release = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.String(1000), nullable=False)
    listed = db.Column(db.String(1000), nullable=False)
    no_reviews = db.Column(db.String(1000), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(1000), nullable=False)
    reviews = db.Column(db.String(1000), nullable=False)
    place = db.Column(db.String(1000), nullable=False)
    playing = db.Column(db.String(1000), nullable=False)
    backlogs = db.Column(db.String(1000), nullable=False)
    wishlist = db.Column(db.String(1000), nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    feedback = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to the login page if not logged in
        return f(*args, **kwargs)
    return decorated_function


@app.route('/collections', methods=['GET'])
@login_required
def collections():
    sort_by = request.args.get('sort_by', 'id')  # Default to 'title' (alphabetical)
    sort_order = request.args.get('sort_order', 'asc')  # Default to ascending

    # Sorting logic
    if sort_by == 'rating':
        sort_column = Game.rating
    elif sort_by == 'release':
        sort_column = Game.release
    elif sort_by == 'title':
        sort_column = Game.title
    else:
        sort_column = Game.id

    # Apply sorting order
    if sort_order == 'desc':
        games = Game.query.order_by(sort_column.desc()).all()
    else:
        games = Game.query.order_by(sort_column.asc()).all()

    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    # games = Game.query.all()
    return render_template('collections.html', games=games)

@app.route('/add', methods=['POST'])
def add_game():
    new_game = Game(
        title = request.form['title'],
        release = request.form['release'],
        team = request.form['team'],
        rating = request.form['rating'],
        listed = request.form['listed'],
        no_reviews = request.form['no_reviews'],
        genres = request.form['genres'],
        summary = request.form['summary'],
        reviews = request.form['reviews'],
        place = request.form['place'],
        playing = request.form['playing'],
        backlogs = request.form['backlogs'],
        wishlist = request.form['wishlist']

    )
    image_file = request.files['image']
    image_filename = None
    if image_file:
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
    db.session.add(new_game)
    db.session.commit()
    return redirect(url_for('collections'))

@app.route('/add')
def add():
    db.session.commit()
    return render_template('add.html')

# Route: Delete a game
@app.route('/delete/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if game:
        db.session.delete(game)
        db.session.commit()
    return redirect(url_for('collections'))

# Route: Edit a game
@app.route('/edit/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    game = Game.query.get(game_id)
    if request.method == 'POST':
        if game:
            game.image = request.form['image']
            game.title = request.form['title']
            game.release = request.form['release']
            game.team = request.form['team']
            game.rating = request.form['rating']
            game.listed = request.form['listed']
            game.no_reviews = request.form['no_reviews']
            game.genres = request.form['genres']
            game.summary = request.form['summary']
            game.reviews = request.form['reviews']
            game.place = request.form['place']
            game.playing = request.form['playing']
            game.backlogs = request.form['backlogs']
            game.wishlist = request.form['wishlist']

            db.session.commit()
        return redirect(url_for('collections'))
    return render_template('edit.html', game=game)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error="Please fill in all fields")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('collections'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists, please choose another", 409
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        username = request.form['username']
        feedback = request.form['feedback']

        new_feedback = Feedback(username=username, feedback=feedback)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('connect', message="Thank you for your feedback!"))
    return render_template('connect.html')

@app.route('/admin/feedback', methods=['GET'])
def admin_feedback():
    if 'user_id' not in session:  # Check if the user is an admin (you can extend this logic)
        return redirect(url_for('login'))  # Admin should be logged in to view feedback
    feedbacks = Feedback.query.all()  # Get all feedback
    return render_template('admin_feedback.html', feedbacks=feedbacks)


if __name__ == '__main__':
    app.run(

            debug=True)