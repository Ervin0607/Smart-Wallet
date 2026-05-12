import requests
from flask import Blueprint, request, jsonify
from decimal import Decimal
from db import get_connection

crypto_bp = Blueprint("crypto", __name__)

@crypto_bp.route("/crypto/prices", methods=["GET"])
def get_supported_crypto():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    coin_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'ADA': 'cardano',
        'XRP': 'ripple'
    }
    
    try:
    
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(coin_map.values()),
            "vs_currencies": "inr"
        }
        
    
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
        
            for symbol, gecko_id in coin_map.items():
                if gecko_id in data and 'inr' in data[gecko_id]:
                    live_price = data[gecko_id]['inr']
                    
                    update_query = """
                        UPDATE SupportedCrypto 
                        SET LiveMarketPrice = %s 
                        WHERE Symbol = %s
                    """
                    cursor.execute(update_query, (live_price, symbol))
            
            conn.commit()
        else:
            print(f"CoinGecko API Error: Status {response.status_code}")
        
            
    except requests.exceptions.RequestException as e:
        print("Network error fetching live prices:", str(e))
    
  
    cursor.execute("SELECT * FROM SupportedCrypto")
    assets = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(assets)


@crypto_bp.route("/crypto/<int:wallet_id>", methods=["GET"])
def get_crypto_assets(wallet_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT CA.AssetID, SC.Symbol, SC.CryptoName, CA.Quantity, SC.LiveMarketPrice
    FROM CryptoAsset CA
    JOIN SupportedCrypto SC ON CA.AssetID = SC.CryptoID
    WHERE CA.WalletID = %s AND CA.Quantity > 0
    """
    cursor.execute(query, (wallet_id,))
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(assets)

@crypto_bp.route("/crypto/buy", methods=["POST"])
def buy_crypto():
    data = request.json
    wallet_id = data.get("wallet_id")
    crypto_id = data.get("crypto_id")
    quantity = Decimal(str(data.get("quantity"))) 
    payment_mode = data.get("payment_mode")
    account_id = data.get("account_id")
    force = data.get("force", False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT LiveMarketPrice FROM SupportedCrypto WHERE CryptoID = %s", (crypto_id,))
        price = cursor.fetchone()["LiveMarketPrice"]
        total_cost = Decimal(str(price)) * Decimal(str(quantity))

        if payment_mode == "Wallet" and not force:
            check_query = """
                SELECT B.LimitAmount, B.SpentAmount 
                FROM Budget B
                JOIN Wallet W ON B.UserID = W.UserID
                WHERE W.WalletID = %s 
                  AND B.StartDate <= CURDATE() 
                  AND B.EndDate >= CURDATE()
            """
            cursor.execute(check_query, (wallet_id,))
            budget = cursor.fetchone()

            if budget:
                limit_amt = Decimal(str(budget["LimitAmount"]))
                spent_amt = Decimal(str(budget["SpentAmount"]))
                projected_spent = spent_amt + total_cost
                remaining_budget = limit_amt - spent_amt

                if projected_spent >= limit_amt:
                    return jsonify({
                        "warning": True,
                        "message": f"Wait! This crypto purchase will exceed your active budget.\n\nYou only have {remaining_budget:.2f} INR remaining to safely spend.\n\nProjected total spent: {projected_spent:.2f} INR (Limit: {limit_amt:.2f} INR).\n\nDo you want to proceed anyway?"
                    }), 200

        if payment_mode == "Bank":
            if not account_id:
                return jsonify({"error": "Please select a bank account."}), 400
                
            cursor.execute("SELECT BankBalance FROM BankAccount WHERE AccountID = %s FOR UPDATE", (account_id,))
            bank = cursor.fetchone()
            if not bank or Decimal(str(bank["BankBalance"])) < total_cost:
                return jsonify({"error": "Insufficient bank balance"}), 400
            
            cursor.execute("UPDATE BankAccount SET BankBalance = BankBalance - %s WHERE AccountID = %s", (total_cost, account_id))
            
            cursor.execute("""
                INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, AccountID, AssetID, Status)
                VALUES (%s, 8, %s, 'Bank Transfer', %s, %s, 'COMPLETED')
            """, (wallet_id, float(total_cost), account_id, crypto_id))

        # --- WALLET PURCHASE LOGIC ---
        elif payment_mode == "Wallet":
            cursor.execute("SELECT Balance FROM Wallet WHERE WalletID = %s FOR UPDATE", (wallet_id,))
            wallet = cursor.fetchone()
            if not wallet or Decimal(str(wallet["Balance"])) < total_cost:
                return jsonify({"error": "Insufficient wallet balance"}), 400

            cursor.execute("""
                INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, AssetID, Status)
                VALUES (%s, 8, %s, 'Wallet Balance', %s, 'COMPLETED')
            """, (wallet_id, float(total_cost), crypto_id))
            
        else:
            return jsonify({"error": "Invalid payment method selected."}), 400

        # --- ADD TO PORTFOLIO ---
        cursor.execute("""
            INSERT INTO CryptoAsset (AssetID, WalletID, Quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Quantity = Quantity + %s
        """, (crypto_id, wallet_id, float(quantity), float(quantity)))

        conn.commit()
        return jsonify({"message": "Crypto purchased successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@crypto_bp.route("/crypto/sell", methods=["POST"])
def sell_crypto():
    data = request.json
    wallet_id = data.get("wallet_id")
    crypto_id = data.get("crypto_id")
    quantity = Decimal(str(data.get("quantity")))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT Quantity FROM CryptoAsset WHERE WalletID = %s AND AssetID = %s FOR UPDATE", (wallet_id, crypto_id))
        asset = cursor.fetchone()
        if not asset or Decimal(str(asset["Quantity"])) < quantity:
            return jsonify({"error": "Insufficient crypto quantity"}), 400

        cursor.execute("SELECT LiveMarketPrice FROM SupportedCrypto WHERE CryptoID = %s", (crypto_id,))
        price = cursor.fetchone()["LiveMarketPrice"]
        total_revenue = Decimal(str(price)) * quantity

        cursor.execute("""
            UPDATE CryptoAsset SET Quantity = Quantity - %s
            WHERE WalletID = %s AND AssetID = %s
        """, (float(quantity), wallet_id, crypto_id))

        cursor.execute("UPDATE Wallet SET Balance = Balance + %s WHERE WalletID = %s", (float(total_revenue), wallet_id))

        cursor.execute("""
            INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, AssetID, Status)
            VALUES (%s, 8, %s, 'Crypto Sale', %s, 'COMPLETED')
        """, (wallet_id, float(total_revenue), crypto_id))

        conn.commit()
        return jsonify({"message": "Crypto sold successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()