from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'designora-secret-key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400
    name = data.get('name', '')
    email = data.get('email', '')
    company = data.get('company', '')
    message = data.get('message', '')

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

    return jsonify({
        'success': True,
        'message': f'Thank you {name}! Your message has been received. We will get back to you soon.'
    })

if __name__ == '__main__':
    is_dev = os.environ.get('REPLIT_DEV_DOMAIN') is not None
    app.run(host='0.0.0.0', port=5000, debug=is_dev)
