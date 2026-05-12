from flask import Blueprint, request, jsonify
from db import get_connection

wallet_bp = Blueprint("wallet", __name__)

@wallet_bp.route("/wallet/<int:user_id>", methods=["GET"])
def get_wallet(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM Wallet
    WHERE UserID = %s
    """

    cursor.execute(query, (user_id,))
    wallet = cursor.fetchone()

    cursor.close()
    conn.close()

    if wallet:
        return jsonify(wallet)

    return jsonify({"error": "Wallet not found"}), 404

@wallet_bp.route("/wallet/topup", methods=["POST"])
def topup():

    data = request.json

    wallet_id = data.get("wallet_id")
    amount = data.get("amount")
    account_id = data.get("account_id")

    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check and Lock Bank Account
        cursor.execute("SELECT BankBalance FROM BankAccount WHERE AccountID = %s FOR UPDATE", (account_id,))
        bank_acc = cursor.fetchone()
        
        if not bank_acc:
            return jsonify({"error": "Bank account not found."}), 404
            
        if float(bank_acc["BankBalance"]) < float(amount):
            return jsonify({"error": "Insufficient bank balance for top-up."}), 400

        # Check and Lock Wallet
        cursor.execute("SELECT Balance FROM Wallet WHERE WalletID = %s FOR UPDATE", (wallet_id,))
        wallet = cursor.fetchone()
        if not wallet:
            return jsonify({"error": "Wallet not found."}), 404

        # Deduct from bank account
        cursor.execute("UPDATE BankAccount SET BankBalance = BankBalance - %s WHERE AccountID = %s", (amount, account_id))
        
        # Add to wallet
        cursor.execute("UPDATE Wallet SET Balance = Balance + %s WHERE WalletID = %s", (amount, wallet_id))

        # Insert Transaction Record
        query = """
        INSERT INTO Transaction
        (WalletID, CategoryID, Amount, PaymentMode, AccountID, Status)
        VALUES (%s,9,%s,'Bank Transfer',%s,'COMPLETED')
        """

        cursor.execute(query, (wallet_id, amount, account_id))
        conn.commit()

        return jsonify({"message": "Wallet topped up successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@wallet_bp.route("/bankaccount/<int:user_id>", methods=["GET"])
def get_bank_accounts(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT AccountID, BankName, AccountNumber, BankBalance FROM BankAccount WHERE UserID = %s", (user_id,))
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(accounts)
