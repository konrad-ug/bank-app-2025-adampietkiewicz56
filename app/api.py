from flask import Flask, request, jsonify
from src.account_registry import AccountRegistry
from src.personal_account import PersonalAccount

app = Flask(__name__)
registry = AccountRegistry()
@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    account = PersonalAccount(data["name"], data["surname"], data["pesel"])
    registry.add_account(account)
    return jsonify({"message": "Account created"}), 201

@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.get_all_accounts()

    accounts_data = [{
        "name": acc.first_name,
        "surname": acc.last_name,
        "pesel": acc.pesel,
        "balance": acc.balance
    } for acc in accounts]

    return jsonify(accounts_data), 200

@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Get account count request received")

    count = len(registry.get_all_accounts())
    return jsonify({"count": count}), 200

@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    account = registry.get_account_by_pesel(pesel)

    if account is None:
        return jsonify({"error": "Account not found"}), 404
    #implementacja powinna znaleźć się tutaj i powinna zwracać dane konta
    return jsonify({"name": account.first_name, "surname": account.last_name, "pesel": account.pesel, "balance": account.balance}), 200

@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    data = request.get_json()
    account = registry.get_account_by_pesel(pesel)

    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    if "name" in data:
        account.first_name = data["name"]
    if "surname" in data:
        account.last_name = data["surname"]

    #implementacja powinna znaleźć się tutaj
    return jsonify({"message": "Account updated"}), 200

@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    account = registry.get_account_by_pesel(pesel)

    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    registry.delete_account(pesel)
    return jsonify({"message": "Account deleted"}), 200
