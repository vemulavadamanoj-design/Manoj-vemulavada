from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# ---------- In-memory storage ----------
# In production, replace with a database (SQLite/Postgres)
db = {
    "transactions": [],  # {id, desc, amount, type, category, date}
    "budgets": {"Food":1500, "Books":2000, "Travel":1200, "Entertainment":1000, "Others":1000},
    "goals": []          # {id, name, target, saved}
}

# ---------- Utility helpers ----------
def fmt_currency(n):
    return f"₹{n:,.2f}"

# ---------- Routes ----------

@app.route("/")
def home():
    return {"message": "Student Finance Manager Backend is running ✅"}

# ---- Transactions ----
@app.route("/transactions", methods=["GET"])
def get_transactions():
    return jsonify(db["transactions"])

@app.route("/transactions", methods=["POST"])
def add_transaction():
    data = request.json
    if not data or "desc" not in data or "amount" not in data:
        return {"error": "Invalid data"}, 400
    
    tx = {
        "id": str(uuid.uuid4())[:8],
        "desc": data["desc"],
        "amount": float(data["amount"]),
        "type": data.get("type", "expense"),
        "category": data.get("category", "Others"),
        "date": data.get("date", datetime.today().strftime("%Y-%m-%d"))
    }
    db["transactions"].append(tx)
    return jsonify(tx), 201

# ---- Budgets ----
@app.route("/budgets", methods=["GET"])
def get_budgets():
    return jsonify(db["budgets"])

@app.route("/budgets", methods=["POST"])
def update_budgets():
    data = request.json
    if not isinstance(data, dict):
        return {"error": "Invalid data"}, 400
    db["budgets"].update(data)
    return jsonify(db["budgets"])

# ---- Goals ----
@app.route("/goals", methods=["GET"])
def get_goals():
    return jsonify(db["goals"])

@app.route("/goals", methods=["POST"])
def add_goal():
    data = request.json
    if "name" not in data or "target" not in data:
        return {"error": "Invalid data"}, 400
    goal = {
        "id": str(uuid.uuid4())[:8],
        "name": data["name"],
        "target": float(data["target"]),
        "saved": 0.0
    }
    db["goals"].append(goal)
    return jsonify(goal), 201

@app.route("/goals/<goal_id>/deposit", methods=["POST"])
def deposit_goal(goal_id):
    for g in db["goals"]:
        if g["id"] == goal_id:
            g["saved"] = min(g["target"], g["saved"] + 100)
            return jsonify(g)
    return {"error": "Goal not found"}, 404

@app.route("/goals/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    db["goals"] = [g for g in db["goals"] if g["id"] != goal_id]
    return {"message": "Goal deleted"}

# ---- Summary / Analytics ----
@app.route("/summary", methods=["GET"])
def get_summary():
    income = sum(t["amount"] for t in db["transactions"] if t["type"] == "income")
    expense = sum(t["amount"] for t in db["transactions"] if t["type"] == "expense")
    balance = income - expense
    return {
        "income": income,
        "expense": expense,
        "balance": balance,
        "formatted": {
            "income": fmt_currency(income),
            "expense": fmt_currency(expense),
            "balance": fmt_currency(balance)
        }
    }

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
