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

