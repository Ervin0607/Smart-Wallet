from flask import Blueprint, request, jsonify
from db import get_connection

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/transaction", methods=["POST"])
def create_transaction():
    data = request.json
    wallet_id = data.get("wallet_id")
    category_id = data.get("category_id")
    amount = float(data.get("amount"))
    
   
    force = data.get("force", False)

    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check and lock wallet balance
        cursor.execute("SELECT Balance FROM Wallet WHERE WalletID = %s FOR UPDATE", (wallet_id,))
        wallet = cursor.fetchone()
        if not wallet:
            return jsonify({"error": "Wallet not found."}), 404
        if float(wallet["Balance"]) < amount:
            return jsonify({"error": "Insufficient wallet balance."}), 400

        if not force:
            check_query = """
                SELECT B.LimitAmount, B.SpentAmount 
                FROM Budget B
                JOIN Wallet W ON B.UserID = W.UserID
                WHERE W.WalletID = %s 
                  AND B.StartDate <= CURDATE() 
                  AND B.EndDate >= CURDATE()
                FOR UPDATE
            """
            cursor.execute(check_query, (wallet_id,))
            budget = cursor.fetchone()

            if budget:
                limit_amt = float(budget["LimitAmount"])
                spent_amt = float(budget["SpentAmount"])
                projected_spent = spent_amt + amount
                remaining_budget = limit_amt - spent_amt
                
                if projected_spent >= limit_amt:
                    return jsonify({
                        "warning": True,
                        "message": f"Wait! This transaction will exceed your budget.\n\nYou only have {remaining_budget:.2f} INR remaining to safely spend.\n\nProjected total spent: {projected_spent:.2f} INR (Limit: {limit_amt:.2f} INR).\n\nDo you want to proceed anyway?"
                    }), 200

        # --- PROCESS TRANSACTION ---
        insert_query = """
        INSERT INTO Transaction
        (WalletID, CategoryID, Amount, PaymentMode, Status)
        VALUES (%s,%s,%s,'Wallet Balance','COMPLETED')
        """
        cursor.execute(insert_query, (wallet_id, category_id, amount))
        conn.commit()

        return jsonify({"message": "Transaction successful"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@transaction_bp.route("/transactions/<int:wallet_id>", methods=["GET"])
def get_transactions(wallet_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT t.TransactionID, t.Amount, t.TransactionDate, t.PaymentMode, t.Status, c.CategoryName 
    FROM Transaction t
    JOIN Category c ON t.CategoryID = c.CategoryID
    WHERE t.WalletID = %s
    ORDER BY t.TransactionDate DESC
    """

    cursor.execute(query, (wallet_id,))
    transactions = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(transactions)
