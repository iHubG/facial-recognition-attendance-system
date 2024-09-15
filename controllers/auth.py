from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    errors = {}
    success_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            errors['username'] = 'Username is required'
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'

        if not errors: 
            if username == 'admin' and password == 'admin12345':
                session['logged_in'] = True
                success_message = 'Login successful! Redirecting...'
            else:
                errors['auth'] = 'Username and Password do not match!'

    return render_template('views/login.html', errors=errors, success_message=success_message)
