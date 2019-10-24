from blogapp import app ,db
from flask import render_template, flash, redirect, url_for, request
from blogapp.forms import LoginForm, RegistrationForm, EditProfileForm, CreatePostForm
from flask_login import current_user, login_user, logout_user, login_required
from blogapp.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime

# Execute this function first when user makes a request to the server
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CreatePostForm()
    posts = Post.query.all()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('New Post has been created!')
        return redirect(url_for('index'))

    return render_template('index.html', title="Home", form=form, posts=posts)

@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):

    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    # If POST request is received
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Check if User exists or password is correct
        if user is None or not user.check_password(form.password.data):
            # Flash is used to display messages which can be
            # retrieved in the templates using get_flashed_messages()
            flash('Invalid Username or Password')
            return redirect(url_for('login'))

        # Log in user if credentials are correct
        login_user(user, remember=form.remember_me.data)
        # If next query argument is provided in the url,
        # redirect user to that url
        next_page = request.args.get('next')
        # If next query argument is not provided or relative path is not provided
        # (full url with domain name is provided), redirect to index
        # Second condition ensures that the redirect stays within the same site as application
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have registered successfully!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

# View Function to display Profile of current logged in user
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

# View Function to edit User Profile who is logged in currently
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # If POST request is made and data is valid
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('edit_profile'))

    # Pre-populate the form fields with details present in the database when GET request is made
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)
