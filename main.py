from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog_body, owner):
        self.title = title
        self.blog_body = blog_body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    posts = Post.query.order_by('-id', owner=owner).all()
    return render_template('blog.html', title="Build-A-Blog", 
        posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    body_error = ''
    if request.method == 'POST':
        post_title = request.form['title']
        blog_body = request.form['blog_body']

        if blog_body == "":
            body_error = 'Please fill in the body'

        if post_title == "":
            title_error = 'Please enter a post title'
        if not body_error and not title_error:
            new_post = Post(post_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            post_id = Post.query.order_by('-id').first()
            return redirect('/viewpost?id={0}'.format(post_id.id))
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, post_title=post_title,
             blog_body=blog_body, title="Build-A-Blog")
    return render_template('newpost.html', title="Build-A-Blog")


@app.route('/viewpost', methods=['POST', 'GET'])
def viewpost():
    if request.method == 'POST':
        id = request.form['id']

    id = request.args.get('id')
    post_id = Post.query.filter_by(id=id).first()

    return render_template('viewpost.html', post_id=post_id, title="Build-A-Blog")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in!")
            return redirect('/')
        else:
            flash('User password is incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #Validate Username
        if len(username) < 3 or len(username) > 30 or " " in username:
            return '<h1>Please enter a valid username</h1>'

        #Validate Password
        if len(password) < 3 or len(password) > 20:
            return '<h1>Make sure your password is at between 3 and 20 characters</h1>'

        #Validate Second Password
        if password != verify:
            verify_error = '<h1>Your passwords do not match</h1>'

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - "Better response message"
            return '<h1>Duplicate user.</h1>'

    return render_template('signup.html')

if __name__ == '__main__':
    app.run()