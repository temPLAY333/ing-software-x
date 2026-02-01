from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from mongoengine import connect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@app.com')

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": os.getenv('CORS_ORIGINS', '*').split(',')}})
api = Api(app)
jwt = JWTManager(app)
mail = Mail(app)

# MongoDB Connection
try:
    # Main Database
    connect(
        db='main_db',
        host=os.getenv('MONGODB_URI'),
        alias='default',
        tls=True,
        tlsAllowInvalidCertificates=False
    )
    
    # Logs Database
    connect(
        db='logs_db',
        host=os.getenv('MONGODB_LOGS_URI'),
        alias='logs',
        tls=True,
        tlsAllowInvalidCertificates=False
    )
    print("✅ Connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

# Import routes
from routes.mensajes_privados import mensajes_privados_bp

# Register blueprints
app.register_blueprint(mensajes_privados_bp, url_prefix='/api')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Backend API',
        'version': '1.0.0'
    }), 200

# Server-Sent Events example endpoint
@app.route('/api/stream', methods=['GET'])
def stream():
    def generate():
        import time
        for i in range(10):
            yield f"data: {{'message': 'Event {i}', 'timestamp': {time.time()}}}\n\n"
            time.sleep(1)
    
    return app.response_class(generate(), mimetype='text/event-stream')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
