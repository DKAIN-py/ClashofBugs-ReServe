from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from routes.datafetch import list_bp, filtersort_bp
app.register_blueprint(list_bp)
app.register_blueprint(filtersort_bp)

# @app.route('/')
# def home():
#     return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True,port=3000)