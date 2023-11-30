from flask import Flask, flash, render_template, request, redirect, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_credential.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'vishnu'


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(UserMixin, db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)


with app.app_context():
    db.create_all()


# HOME_PAGE
@app.route('/')
def home():
    return render_template("home.html")


# REGISTER PAGE
@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['uname']
        email = request.form['email']
        password = request.form['pass']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already taken', 'error')
        else:
            hash_pass = generate_password_hash(password, method='pbkdf2:sha256', salt_length=5)
            new_user = User(username=username, email=email, password=hash_pass)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return render_template("welcome.html", name=username.upper())
    return render_template("sign_up.html")


# LOGIN PAGE
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    username = request.form.get('username')
    password = request.form.get('password')

    result = db.session.execute(db.select(User).where(User.username == username))
    user = result.scalar()
    # user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('welcome'))
    else:
        flash("Invalid username or password")
    return render_template("login.html")


@app.route('/welcome')
@login_required
def welcome():
    return render_template("welcome.html", name=current_user.username.upper())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# HOME_PAGE
@app.route('/home')
def home1():
    return render_template("home.html")


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/mementopython3-english.pdf")


if __name__ == '__main__':
    app.run(debug=True)
