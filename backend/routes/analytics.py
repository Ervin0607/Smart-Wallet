from flask import Blueprint, jsonify
from db import get_connection

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics/<int:user_id>", methods=["GET"])
def spending_analytics(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT C.CategoryName, SUM(T.Amount) AS TotalSpent
    FROM Transaction T
    JOIN Wallet W ON T.WalletID = W.WalletID
    JOIN Category C ON T.CategoryID = C.CategoryID
    WHERE W.UserID = %s AND T.Status = 'COMPLETED'
      AND T.CategoryID != 9 AND T.PaymentMode != 'Received Transfer'
    GROUP BY C.CategoryName
    ORDER BY TotalSpent DESC
    """

    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(data)

@analytics_bp.route("/analytics/budget/<int:user_id>", methods=["GET"])
def budget_usage(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Updated to fetch ALL budgets for the user
    query = """
    SELECT BudgetID, LimitAmount, SpentAmount, StartDate, EndDate
    FROM Budget
    WHERE UserID = %s
    ORDER BY StartDate DESC
    """

    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(data)

@analytics_bp.route("/analytics/networth/<int:user_id>", methods=["GET"])
def net_worth(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT Balance FROM Wallet WHERE UserID = %s", (user_id,))
    wallet = cursor.fetchone()
    wallet_bal = float(wallet["Balance"]) if wallet else 0.0

    cursor.execute("SELECT SUM(BankBalance) as TotalBank FROM BankAccount WHERE UserID = %s", (user_id,))
    bank = cursor.fetchone()
    bank_bal = float(bank["TotalBank"]) if bank and bank["TotalBank"] else 0.0

    crypto_query = """
    SELECT SUM(CA.Quantity * SC.LiveMarketPrice) as TotalCrypto
    FROM CryptoAsset CA
    JOIN SupportedCrypto SC ON CA.AssetID = SC.CryptoID
    JOIN Wallet W ON CA.WalletID = W.WalletID
    WHERE W.UserID = %s
    """
    cursor.execute(crypto_query, (user_id,))
    crypto = cursor.fetchone()
    crypto_bal = float(crypto["TotalCrypto"]) if crypto and crypto["TotalCrypto"] else 0.0

    cursor.close()
    conn.close()

    total_net_worth = wallet_bal + bank_bal + crypto_bal

    return jsonify({
        "Wallet": wallet_bal,
        "Bank": bank_bal,
        "Crypto": crypto_bal,
        "TotalNetWorth": total_net_worth
    })