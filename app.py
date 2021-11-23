from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "placeholder"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def root():
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register_user():
    if 'user_id' in session:
        return redirect(f"/users/{session['user_id']}")
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
            session['user_id'] = new_user.username
            return redirect(f'/users/{new_user.username}')
        except IntegrityError:
            flash("Username taken")
        return redirect('/register')
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(f"/users/{session['user_id']}")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)
        if user:
            session['user_id'] = user.username
            return redirect(f'/users/{user.username}')
    return render_template('login.html', form=form)

@app.route('/secret')
def show_secret():
    if 'user_id' in session:
        return render_template('secret.html')
    flash("Must be logged in to view this")
    return redirect('/login')

@app.route('/users/<username>', methods=['GET','POST'])
def show_user(username):
    if 'user_id' in session:
        user = User.query.get_or_404(username)
        return render_template('user.html', user=user)
    flash("Must be logged in to view this page")
    return redirect('/login')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if session['user_id'] == username:
        user = User.query.get_or_404(username)
        db.session.delete(user)
        try:
            db.session.commit()
            flash("User deleted successfully")
            session.pop('user_id')
        except:
            flash("Error deleting user")
        return redirect(f'/register')
    flash("You can only delete your own account.")
    return redirect(f'/users/{username}')

@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def add_feedback(username):
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title,content=content,username=session['user_id'])
        db.session.add(new_feedback)
        try:
            db.session.commit()
            flash("Feedback submitted successfully!")
        except:
            flash("Error submitting feedback")
        return redirect(f'/users/{username}')
    return render_template('feedback-add.html',form=form, user=user)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET','POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(feedback.username)
    if session['user_id'] == feedback.username:
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.add(feedback)
            try:
                db.session.commit()
                flash("Feedback edited successfully!")
            except:
                flash("Error editing feedback")
            return redirect(f'/users/{feedback.username}')
    else:
        flash("You must be logged in as this user to edit this feedback")
        return redirect('/users/{feedback.username}')
    return render_template('feedback-edit.html',form=form, user=user)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(feedback.username)
    if session['user_id'] == feedback.username:
        db.session.delete(feedback)
        try:
            db.session.commit()
            flash("Feedback deleted successfully")
        except:
            flash("Error deleting feedback")
        return redirect(f'/users/{user.username}')
    flash("You can only delete feedback posted from your account.")
    return redirect(f'/users/{user.username}')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


