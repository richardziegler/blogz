from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.String(1000))

    def __init__(self, title, blog_body):
        self.title = title
        self.blog_body = blog_body

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    posts = Post.query.order_by('-id').all()
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
            new_post = Post(post_title, blog_body)
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


if __name__ == '__main__':
    app.run()