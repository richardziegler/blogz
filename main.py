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

@app.before_request
def require_login():
    allowed_routes = ['blog', 'login', 'signup', 'viewpost', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    owner = User.query.all()
    posts = Post.query.order_by('-id').all()
    return render_template('blog.html', title="Build-A-Blog", 
        posts=posts, owner=owner)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    body_error = ''
    owner = User.query.filter_by(username=session['username']).first()
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
    username_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        user_not_exist_error = ''
        
        if username == "":
            username_error = 'Please enter a username'

        if password == "":
            password_error = 'Please enter a valid password'

        if not user and username != "":
            user_not_exist_error = 'This username does not exist'

        if user and user.password != password:
            password_error = 'The password is incorrect'

        if not username_error and not password_error and not user_not_exist_error:
            if user and user.password == password:
                session['username'] = username
                flash("Logged in!")
                return redirect('/newpost')
        else:
            return render_template('login.html', password_error=password_error, username_error=username_error,
             user_not_exist_error=user_not_exist_error, title="User Login")

    return render_template('login.html', title="User Login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''
    existing_user_error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        #Validate Username
        if len(username) < 3 or len(username) > 30 or " " in username:
            username_error = 'Please enter a valid username'

        #Validate Password
        if len(password) < 3 or len(password) > 20:
            password_error = 'Make sure your password is at between 3 and 20 characters'

        #Validate Second Password
        if password != verify:
            verify_error = 'Your passwords do not match'

        if existing_user:
            existing_user_error = 'This username already exists'

        
        if not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error,
             verify_error=verify_error, existing_user_error=existing_user_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()