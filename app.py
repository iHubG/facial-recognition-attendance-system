from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def login():
    errors = {}
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate username and password
        if not username:
            errors['username'] = 'Username is required.'
        if not password:
            errors['password'] = 'Password is required.'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long.'

        if not errors:
            # Process login (authentication logic here)
            return redirect(url_for('success'))

    return render_template('views/login.html', errors=errors)

@app.route('/success')
def success():
    return 'Login successful!'

if __name__ == '__main__':
    app.run(debug=True)
