from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- Flask App Setup ---
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tint.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"  # Required for session security

db = SQLAlchemy(app)

# --- Flask Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects to login if not logged in


# --- Tint Table (Notes/Posts Table) ---
class Tint(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f"{self.Sno} - {self.title}"


# --- User Table for Authentication ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# --- Login Loader (Required by Flask-Login) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Home Route ---
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        tint = Tint(title=title, desc=desc)
        db.session.add(tint)
        db.session.commit()
        return redirect(url_for("home"))
    allTint = Tint.query.order_by(Tint.date_created.desc()).all()
    return render_template("index.html", allTint=allTint, user=current_user)


# --- Update Route ---
@app.route("/update/<int:Sno>", methods=["GET", "POST"])
@login_required
def update(Sno):
    tint = Tint.query.filter_by(Sno=Sno).first()
    if not tint:
        return "Record not found"
    if request.method == "POST":
        tint.title = request.form["title"]
        tint.desc = request.form["desc"]
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("update.html", tint=tint, user=current_user)


# --- Delete Route ---
@app.route("/delete/<int:Sno>")
@login_required
def delete(Sno):
    tint = Tint.query.filter_by(Sno=Sno).first()
    if not tint:
        return "Record not found"
    db.session.delete(tint)
    db.session.commit()
    return redirect(url_for("home"))


# --- Register Route ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists! Try logging in."

        # ✅ Fixed hash method
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")



# --- Login Route ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return "Invalid credentials! Try again."
    return render_template("login.html")


# --- Logout Route ---
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# --- Dashboard Route ---
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)