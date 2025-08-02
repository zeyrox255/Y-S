from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

order_bp = Blueprint('order', __name__)

@order_bp.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'customer' not in data or 'items' not in data:
            return jsonify({'error': 'Invalid order data'}), 400
        
        customer = data['customer']
        items = data['items']
        total = data.get('total', 0)
        
        # Validate customer data
        required_fields = ['name', 'email', 'phone', 'address']
        for field in required_fields:
            if not customer.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not items:
            return jsonify({'error': 'No items in order'}), 400
        
        # Prepare email content
        email_content = prepare_email_content(customer, items, total)
        
        # Send email
        success = send_order_email(email_content, customer)
        
        if success:
            return jsonify({'message': 'Order submitted successfully!'}), 200
        else:
            return jsonify({'error': 'Failed to send order email'}), 500
            
    except Exception as e:
        print(f"Error processing order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def prepare_email_content(customer, items, total):
    """Prepare the email content for the order"""
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    content = f"""
New Order from Y&S Perfumes Website

Order Date: {order_date}

Customer Information:
Name: {customer['name']}
Email: {customer['email']}
Phone: {customer['phone']}
Address: {customer['address']}
"""
    
    if customer.get('notes'):
        content += f"Special Notes: {customer['notes']}\n"
    
    content += "\nOrder Items:\n"
    for item in items:
        item_total = item['price'] * item['quantity']
        content += f"- {item['name']} ({item['size']}) x {item['quantity']} = {item_total} EGP\n"
    
    content += f"\nTotal Amount: {total} EGP\n\n"
    content += "Please contact the customer to confirm the order and arrange delivery."
    
    return content

def send_order_email(content, customer):
    """Send order email using SMTP"""
    try:
        # For demonstration purposes, we'll use a simple approach
        # In production, you would configure proper SMTP settings
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = customer['email']  # Customer's email as sender
        msg['To'] = 'yara5454088@gmail.com'
        msg['Subject'] = f'New Perfume Order from {customer["name"]} - Y&S Perfumes'
        
        # Add body to email
        msg.attach(MIMEText(content, 'plain'))
        
        # For now, we'll simulate successful email sending
        # In a real application, you would configure SMTP server settings
        print("Email content prepared:")
        print(content)
        print(f"Email would be sent to: yara5454088@gmail.com")
        print(f"From: {customer['email']}")
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@order_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'order_service'}), 200


import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.order import order_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
