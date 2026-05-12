from flask import Blueprint, jsonify
from db import get_connection
from flask import request
from datetime import datetime, date

budget_bp = Blueprint("budget", __name__)

@budget_bp.route("/budget/<int:user_id>", methods=["GET"])
def get_budget(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
    
        update_query = """
            UPDATE Budget 
            SET Status = 'Finished' 
            WHERE UserID = %s AND EndDate < CURDATE() AND Status != 'Finished'
        """
        cursor.execute(update_query, (user_id,))
        conn.commit()

    
        query = "SELECT * FROM Budget WHERE UserID = %s ORDER BY StartDate DESC"
        cursor.execute(query, (user_id,))
        budgets = cursor.fetchall()

        return jsonify(budgets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@budget_bp.route("/alerts/<int:user_id>", methods=["GET"])
def get_alerts(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT A.AlertID, A.AlertMessage, A.TriggerDate, A.IsREAD
    FROM Alert A
    JOIN Budget B ON A.BudgetID = B.BudgetID
    WHERE B.UserID = %s
    ORDER BY A.TriggerDate DESC
    """

    cursor.execute(query, (user_id,))
    alerts = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(alerts)

@budget_bp.route("/alerts/read/<int:alert_id>", methods=["PUT"])
def mark_alert_read(alert_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE Alert
    SET IsREAD = TRUE
    WHERE AlertID = %s
    """

    cursor.execute(query, (alert_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Alert marked as read"})


@budget_bp.route("/budget", methods=["POST"])
def create_budget():
    data = request.json
    user_id = data.get("user_id")
    limit_amount = float(data.get("limit_amount"))
    start_date = data.get("start_date")
    end_date = data.get("end_date")


    if limit_amount <= 0:
        return jsonify({"error": "Budget limit must be greater than zero."}), 400


    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        today = date.today()

        if end_date_obj < today:
            return jsonify({"error": "End date cannot be in the past."}), 400
        
        if end_date_obj <= start_date_obj:
            return jsonify({"error": "End date must be strictly after the start date."}), 400
    except ValueError:
         return jsonify({"error": "Invalid date format."}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO Budget (UserID, LimitAmount, SpentAmount, StartDate, EndDate, Status)
        VALUES (%s, %s, 0, %s, %s, 'Active')
        """
        cursor.execute(query, (user_id, limit_amount, start_date, end_date))
        conn.commit()

        return jsonify({"message": "Budget created successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        

@budget_bp.route("/budget/<int:budget_id>", methods=["PUT"])
def update_budget(budget_id):
    data = request.json
    limit_amount = float(data.get("limit_amount"))
    if limit_amount <= 0:
        return jsonify({"error": "Budget limit must be greater than zero."}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT SpentAmount FROM Budget WHERE BudgetID = %s", (budget_id,))
        budget = cursor.fetchone()
        
        if not budget:
            return jsonify({"error": "Budget not found"}), 404
            
        if limit_amount < float(budget["SpentAmount"]):
            return jsonify({"error": f"Limit cannot be lower than the already spent amount ({budget['SpentAmount']} INR)."}), 400

    
        query = "UPDATE Budget SET LimitAmount = %s WHERE BudgetID = %s"
        cursor.execute(query, (limit_amount, budget_id))
        conn.commit()

        return jsonify({"message": "Budget limit updated successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@budget_bp.route("/budget/<int:budget_id>", methods=["DELETE"])
def delete_budget(budget_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM Budget WHERE BudgetID = %s"
        cursor.execute(query, (budget_id,))
        conn.commit()

        return jsonify({"message": "Budget deleted successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

