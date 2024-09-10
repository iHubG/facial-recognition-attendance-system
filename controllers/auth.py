from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    errors = {}
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
            return redirect(url_for('dashboard.dashboard'))

    return render_template('views/login.html', errors=errors)
