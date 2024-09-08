from flask import Flask, render_template, redirect, url_for
from controllers.auth import auth_bp
from controllers.dashboard import dashboard_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/admin')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('views/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)

# Print all routes
for rule in app.url_map.iter_rules():
    print(rule)
