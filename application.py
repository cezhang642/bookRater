import os
import requests

from flask import Flask, session, render_template, request, redirect, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from xml.etree import ElementTree

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#remember to deal with sessions
@app.route("/", methods=["GET","POST"])
@app.route('/newlogin/', methods=['GET', 'POST'])
def new_login():
    if request.method == "POST":
        the_user = request.form.get('username')
        the_pass = request.form.get('password')
        repeat_users = db.execute("SELECT * FROM users WHERE user_id = (:a) ", {"a":the_user}).fetchall()
        if repeat_users:
            print("username alrady exist")
            return redirect('')
        else:
            db.execute("INSERT INTO users (user_id, user_pass) VALUES (:u,:p)", {"u":the_user,"p":the_pass})
            # make a message that user already exists later
            db.commit()
            return redirect('/home')
    return render_template('login.html', template_folder='templates')

@app.route("/", methods=["GET","POST"])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        the_user = request.form.get('username')
        the_pass = request.form.get('password')
        repeat_users = db.execute("SELECT * FROM users WHERE user_id = (:a)", {"a":the_user}).fetchall()
        if repeat_users:
            valid_pass = db.execute("SELECT * FROM users WHERE user_pass = (:b)", {"b":the_pass}).fetchall()
            if valid_pass:
                return redirect('/home')
            else:
                print("incorrect password")
                return redirect('')
        else:
            print("make new account")
            return redirect('')
    return render_template('login.html', template_folder='templates')


@app.route("/home", methods=["GET","POST"])
@app.route('/home/', methods=['GET', 'POST'])
def home():
    all_books = ""
    if request.method == "POST":
        user_input = request.form.get('inputText')
        api_key = "bH4Y0etz0qZR0NjnEJx1A"
        res = requests.get("https://www.goodreads.com/search/index.xml", params={"q": user_input, "key": api_key})
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")

        root = ElementTree.fromstring(res.content)
        for title in root.iter('*'):
            book_title = title.find('title')
            if book_title is not None:
                all_books += (book_title.text)
    return render_template('home.html', template_folder='templates', all_books=all_books)
