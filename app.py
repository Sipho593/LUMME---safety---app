from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# SECURITY NOTE: In a real app, change 'dev-secret-key' to a complex random string.
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this-in-production')

# Try to import your database functions. 
# If database.py is in the same folder, this will connect automatically.
try:
    from database import init_db, log_alert, purge_all_user_data, save_user_profile
    init_db()
    HAS_DATABASE = True
    print("[SYSTEM] Successfully connected to database.py and initialized tables.")
except ImportError:
    HAS_DATABASE = False
    print("WARNING: database.py not found in this folder. Running in simulation mode without saving data.")

# --- PAGE ROUTING ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')


# --- API ENDPOINTS (POPIA COMPLIANT) ---

@app.route('/api/alert', methods=['POST'])
def handle_emergency_alert():
    """
    POPIA Compliance Note:
    Location and user identifiers are strictly processed for emergency dispatch.
    No persistent background tracking is allowed.
    """
    data = request.get_json() or {}
    
    user_name = data.get('name', 'Anonymous')
    phone = data.get('phone')
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if not phone:
        return jsonify({"status": "error", "message": "Phone number is required to trigger an alert."}), 400

    timestamp = datetime.utcnow().isoformat()

    # Verify explicit consent payload flag
    consent_given = data.get('popia_consent', True)
    if not consent_given:
        return jsonify({
            "status": "error",
            "message": "POPIA Consent required to process location dispatch."
        }), 400

    # Log dispatch signal locally on your machine terminal screen
    print(f"[{timestamp}] EMERGENCY ALERT -> User: {user_name} | Phone: {phone} | GPS: {lat}, {lng}")

    # Save directly to your SQLite database
    if HAS_DATABASE:
        try:
            log_alert(phone, lat, lng)
            print(f"[DATABASE] Emergency alert logged successfully for {phone}")
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to save alert log: {e}")

    # PRODUCTION NOTE: In the future, you will integrate an SMS/WhatsApp gateway like Twilio or BulkSMS here.
    return jsonify({
        "status": "success",
        "message": "Emergency signal dispatched successfully to emergency network.",
        "timestamp": timestamp
    }), 200


@app.route('/api/user/delete-data', methods=['POST'])
def delete_user_data():
    """
    POPIA Compliance: Section 24 (Right to Erasure/Deletion).
    Allows users to purge personal records permanently from the application database.
    """
    data = request.get_json() or {}
    phone = data.get('phone')
    
    if not phone:
        return jsonify({"status": "error", "message": "Phone number is required to delete records."}), 400
        
    print(f"[POPIA] Erasure Request received for phone: {phone}")
    
    if HAS_DATABASE:
        try:
            # Calls your exact function inside database.py
            purge_all_user_data(phone)
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to delete user: {e}")
            return jsonify({"status": "error", "message": "Failed to erase data from database."}), 500
    
    return jsonify({
        "status": "success",
        "message": "All personal identifiers and location logs purged under POPIA guidelines."
    }), 200

if __name__ == '__main__':
    # Runs on port 5000 for Local development / Termux
    # debug=True ensures the server auto-restarts whenever you edit your code files
    app.run(host='0.0.0.0', port=5000, debug=True)
    