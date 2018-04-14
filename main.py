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
    posted = db.Column(db.Boolean)

    def __init__(self, title, blog_body):
        self.title = title
        self.blog_body = blog_body
        self.posted = False


@app.route('/', methods=['POST', 'GET'])
def index():

    posts = Post.query.filter_by(posted=False).all()
    completed_posts = Post.query.filter_by(posted=True).all()
    return render_template('blog.html', title="Your Blog!", 
        posts=posts, completed_posts=completed_posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    body_error = ''
    if request.method == 'POST':
        title = request.form['title']
        blog_body = request.form['blog_body']

        if blog_body == "":
            body_error = 'Please fill in the body'

        if title == "":
            title_error = 'Please enter a post title'
        if not body_error and not title_error:
            new_post = Post(title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
    return render_template('newpost.html')


@app.route('/delete-post', methods=['POST'])
def delete_task():

    post_id = int(request.form['post-id'])
    post = Post.query.get(post_id)
    post.posted = True
    db.session.add(post)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()