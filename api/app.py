from flask import Flask
from flask_cors import CORS
from routes import api_bp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Регистрация blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)