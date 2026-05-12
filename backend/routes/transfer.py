from flask import Blueprint, request, jsonify
from db import get_connection
import bcrypt
import re

transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.route("/transfer", methods=["POST"])
def process_transfer():
    data = request.json
    sender_id = data.get("sender_id")
    recipient_input = data.get("recipient_id")  
    payment_via = data.get("payment_via")       
    amount = float(data.get("amount", 0))       
    password = data.get("password")
    
    category_id = data.get("category_id", 1) 
    
    force = data.get("force", False)

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero."}), 400

    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor(dictionary=True)

    try:
        # VERIFY PASSWORD
        cursor.execute("SELECT PasswordHash FROM User WHERE UserID = %s", (sender_id,))
        user = cursor.fetchone()
        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["PasswordHash"].encode("utf-8")):
            return jsonify({"error": "Incorrect password."}), 401

        # GET SENDER WALLET FOR UPDATE
        cursor.execute("SELECT WalletID, Balance FROM Wallet WHERE UserID = %s FOR UPDATE", (sender_id,))
        sender_wallet = cursor.fetchone()
        if not sender_wallet:
            return jsonify({"error": "Sender wallet not found."}), 404
        sender_wallet_id = sender_wallet["WalletID"]

        # PARSE & GET RECIPIENT WALLET FOR UPDATE
        match = re.search(r'\d+', str(recipient_input))
        if not match:
            return jsonify({"error": "Invalid recipient format. Please enter their ID (e.g., USER-5)."}), 400
        recipient_user_id = int(match.group())

        if sender_id == recipient_user_id:
            return jsonify({"error": "You cannot send money to yourself."}), 400

        cursor.execute("SELECT WalletID FROM Wallet WHERE UserID = %s FOR UPDATE", (recipient_user_id,))
        recipient_wallet = cursor.fetchone()
        if not recipient_wallet:
            return jsonify({"error": "Recipient not found in the system."}), 404
        recipient_wallet_id = recipient_wallet["WalletID"]

        # PRE-FLIGHT BUDGET CHECK
        if payment_via == "wallet" and not force:
            check_query = """
                SELECT B.LimitAmount, B.SpentAmount 
                FROM Budget B
                WHERE B.UserID = %s 
                  AND B.StartDate <= CURDATE() 
                  AND B.EndDate >= CURDATE()
            """
            cursor.execute(check_query, (sender_id,))
            budget = cursor.fetchone()

            if budget:
                limit_amt = float(budget["LimitAmount"])
                spent_amt = float(budget["SpentAmount"])
                projected_spent = spent_amt + amount
                remaining_budget = limit_amt - spent_amt

                if projected_spent > limit_amt:
                    return jsonify({
                        "warning": True,
                        "message": f"Wait! This transfer will exceed your active budget.\n\nYou only have ₹{remaining_budget:.2f} remaining to safely spend.\nProjected total spent: ₹{projected_spent:.2f} (Limit: ₹{limit_amt:.2f}).\n\nDo you want to proceed anyway?"
                    }), 200

        # PROCESS SENDER DEDUCTION
        asset_id = data.get("asset_id")

        if payment_via == "wallet":
            if float(sender_wallet["Balance"]) < amount:
                return jsonify({"error": "Insufficient wallet balance."}), 400
            payment_mode_str = 'Wallet Balance'
            # Trigger handles Wallet & Budget deduction for 'Wallet Balance'
            
        elif payment_via == "bank":
            cursor.execute("SELECT AccountID, BankBalance FROM BankAccount WHERE UserID = %s FOR UPDATE", (sender_id,))
            bank_acc = cursor.fetchone()
            if not bank_acc or float(bank_acc["BankBalance"]) < amount:
                return jsonify({"error": "Insufficient bank balance."}), 400
            cursor.execute("UPDATE BankAccount SET BankBalance = BankBalance - %s WHERE AccountID = %s", (amount, bank_acc["AccountID"]))
            payment_mode_str = 'Bank Transfer'

        elif payment_via == "crypto":
            if not asset_id:
                return jsonify({"error": "No crypto asset selected."}), 400
            
            cursor.execute("SELECT LiveMarketPrice FROM SupportedCrypto WHERE CryptoID = %s", (asset_id,))
            crypto_info = cursor.fetchone()
            if not crypto_info or float(crypto_info["LiveMarketPrice"]) <= 0:
                return jsonify({"error": "Invalid crypto asset or price unavailable."}), 400
            
            live_price = float(crypto_info["LiveMarketPrice"])
            crypto_needed = amount / live_price
            
            cursor.execute("SELECT Quantity FROM CryptoAsset WHERE WalletID = %s AND AssetID = %s FOR UPDATE", (sender_wallet_id, asset_id))
            crypto_asset = cursor.fetchone()
            
            if not crypto_asset or float(crypto_asset["Quantity"]) < crypto_needed:
                return jsonify({"error": "Insufficient crypto quantity to cover the transfer amount."}), 400
                
            cursor.execute("UPDATE CryptoAsset SET Quantity = Quantity - %s WHERE WalletID = %s AND AssetID = %s", (crypto_needed, sender_wallet_id, asset_id))
            payment_mode_str = 'Crypto Transfer'

        else:
             return jsonify({"error": "Invalid payment method selected."}), 400

        # CREDIT RECIPIENT WALLET
        cursor.execute("UPDATE Wallet SET Balance = Balance + %s WHERE WalletID = %s", (amount, recipient_wallet_id))

        # LOG SENDER TRANSACTION (Amount is positive, trigger deducts if Wallet Balance)
        if payment_via == "crypto":
            cursor.execute("""
                INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, AssetID, Status)
                VALUES (%s, %s, %s, %s, %s, 'COMPLETED')
            """, (sender_wallet_id, category_id, amount, payment_mode_str, asset_id))
        else:
            cursor.execute("""
                INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, Status)
                VALUES (%s, %s, %s, %s, 'COMPLETED')
            """, (sender_wallet_id, category_id, amount, payment_mode_str))

        # LOG RECIPIENT TRANSACTION 
        cursor.execute("""
            INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, Status)
            VALUES (%s, %s, %s, 'Received Transfer', 'COMPLETED')
        """, (recipient_wallet_id, category_id, amount))

        conn.commit()
        return jsonify({"message": "Transfer successful!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()