from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from classes import *

app.secret_key = 'ashsjksadnjjw12sds2'

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def authors():
    users = User.query.all()
    return render_template('index.html',title="Build a Blog!", users=users)

@app.route('/post', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_post = request.form['blog']
        title_post = request.form['title']
        if blog_post and title_post:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_post, title_post, owner)
            db.session.add(new_blog)
            db.session.commit()
            id = str(new_blog.id)
            return redirect('/blog?id=' + id)
        else:
            error = "Both Title and Body must be filled out"
            return render_template("post.html", title="Build a Blog!", error=error)

    
    return render_template('post.html',title="Build a Blog!")


@app.route('/blog', methods=['POST', 'GET'])
def blogs():

    if request.args.get("id"):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template("individual.html", post=blog)

    elif request.args.get('userid'):
        id = request.args.get('userid')
        usernames = User.query.filter_by(id=id)
        owner_id = Blog.query.filter_by(id=id).first().owner_id
        users_blogs = Blog.query.filter_by(owner_id=id).all()
        return render_template("singleuser.html", post=users_blogs, id=id)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        
        username_error = ''
        password_error = ''
        verifypass_error = ''
        email_error = ''
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username is None:
            username_error += 'This is a required field.'
        if password is None:
            password_error += 'This is a required field.'
        if verify is None:
            verifypass_error += 'This is a required field.'
        
        
        if len(password) < 3 or len(password) > 20:
            password_error += 'This entry is not valid.'
        

        if verify != password:
            verifypass_error += 'This does not match.'
        
        if username is not "" and len(username) < 3 or len(username) > 20:
            username_error += 'This entry is not valid.'
        
        
        if username is not "" and " " in username:
            username_error += 'This entry is not valid.'
        
        if username is not "" and username.count("@") != 1:
            username_error += 'This entry is not valid.'

        if username is not "" and username.count(".") != 1:
            username_error += 'This entry is not valid.'
        
        if len(verifypass_error) > 1 or len(password_error) > 1 or len(username_error) > 1:
            return render_template("signup.html", username = username, password_error=password_error, verifypass_error=verifypass_error, username_error=username_error)
        else:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/post')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        password = User.query.filter_by(password=password)
        if user and password:
            session['username'] = username
            flash("Logged in", 'info')
            return redirect('/post')
        else:
            flash('User password incorrect, or user does not exist', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    app.run()