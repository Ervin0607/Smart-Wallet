from flask import Blueprint, request, jsonify
from db import get_connection
import bcrypt

auth_bp = Blueprint("auth", __name__)

# REGISTER USER
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    account_number = data.get("account_number")

    if not name or not email or not password or not account_number:
        return jsonify({"error": "All fields including Account Number are required."}), 400

    # HASH PASSWORD
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if dummy account exists
        cursor.execute("SELECT * FROM DummyBank WHERE AccountNumber = %s", (account_number,))
        dummy_bank = cursor.fetchone()

        if not dummy_bank:
            return jsonify({"error": "Account does not exist. Please provide a valid dummy bank account."}), 400

        # Check existing email
        cursor.execute("SELECT UserID FROM User WHERE Email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email is already registered."}), 409

        # 1. Insert User
        query = """
        INSERT INTO User (Name, Email, PasswordHash, Phone)
        VALUES (%s,%s,%s,%s)
        """
        cursor.execute(query, (name, email, hashed_password.decode(), phone))
        user_id = cursor.lastrowid
        
        # 2. Insert Wallet
        cursor.execute("INSERT INTO Wallet (UserID, Balance, Currency) VALUES (%s, 0.00, 'INR')", (user_id,))
        wallet_id = cursor.lastrowid

        # 3. Insert user's BankAccount using details from DummyBank
        bank_query = """
        INSERT INTO BankAccount (UserID, WalletID, AccountNumber, BankName, IFSC_Code, BankBalance)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(bank_query, (
            user_id, wallet_id, 
            dummy_bank["AccountNumber"], dummy_bank["BankName"], 
            dummy_bank["IFSC_Code"], dummy_bank["InitialBalance"]
        ))

        # 4. Remove the account from DummyBank so it's not reused
        cursor.execute("DELETE FROM DummyBank WHERE DummyAccountID = %s", (dummy_bank["DummyAccountID"],))

        conn.commit()

        return jsonify({"message": "User registered successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# LOGIN USER
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM User WHERE Email = %s"

    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:

        stored_hash = user["PasswordHash"]

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):

            return jsonify({
                "message": "Login successful",
                "user": user
            })

    return jsonify({"error": "Invalid credentials"}), 401

# GET USER DETAILS
@auth_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT UserID, Name, Email, Phone
    FROM User
    WHERE UserID = %s
    """

    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify(user)

    return jsonify({"error": "User not found"}), 404
