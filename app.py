from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt 

app=Flask(__name__) # creating an instance of the Flask class
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)
app.secret_key ='secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

@app.route('/') # defining a route for the home page
def home():
    return render_template('index.html') # rendering the index.html template

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or name.strip() == "":
            return render_template("register.html", error="Name cannot be empty")

        if not email or email.strip() == "":
            return render_template("register.html", error="Email cannot be empty")

        if not password or password.strip() == "":
            return render_template("register.html", error="Password cannot be empty")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters long")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template("register.html", error="Email already registered")
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template("register.html")

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template('login.html', error='Email not registered')

        if not user.check_password(password):
            return render_template('login.html', error='Incorrect password')

        session['email'] = user.email
        return redirect('/dashboard')

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template("dashboard.html", user=user)
    return redirect('/login')

@app.route('/logout')
def logout():
          
          session.pop('email',None)
          return redirect('/login') 

if __name__ == '_main_':
    app.run() # running the Flask application in debug mode