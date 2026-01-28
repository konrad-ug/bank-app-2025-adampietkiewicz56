from flask import Flask, request, jsonify
from src.account_registry import AccountRegistry
from src.personal_account import PersonalAccount
from src.mongo_repository import MongoAccountsRepository

app = Flask(__name__)
registry = AccountRegistry()
mongo_repo = MongoAccountsRepository()
@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    
    # Sprawdź czy PESEL już istnieje
    if registry.account_with_pesel_exists(data["pesel"]):
        return jsonify({
            "error": f"Account with PESEL {data['pesel']} already exists"
        }), 409  # 409 Conflict
    
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


@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer(pesel):
    """Endpoint do przelewów - incoming, outgoing, express"""
    account = registry.get_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = data.get("amount")
    transfer_type = data.get("type")
    
    # Sprawdź czy type jest poprawny
    valid_types = ["incoming", "outgoing", "express"]
    if transfer_type not in valid_types:
        return jsonify({
            "error": f"Invalid transfer type. Must be one of: {valid_types}"
        }), 400  # Bad Request
    
    # Wykonaj przelew
    if transfer_type == "incoming":
        account.incoming_transfer(amount)
        return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200
    
    elif transfer_type == "outgoing":
        old_balance = account.balance
        account.outgoing_transfer(amount)
        
        if account.balance == old_balance:  # Nie udało się
            return jsonify({"error": "Insufficient funds"}), 422
        
        return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200
    
    elif transfer_type == "express":
        # Sprawdź czy jest metoda express dla tego konta
        if hasattr(account, 'express_outgoing_pers'):
            old_balance = account.balance
            account.express_outgoing_pers(amount)
            
            if account.balance == old_balance:  # Nie udało się
                return jsonify({"error": "Insufficient funds"}), 422
            
            return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200
        else:
            return jsonify({
                "error": "This account type does not support express transfers"
            }), 400

@app.route("/api/accounts/save", methods=['POST'])
def save_accounts():
    """Zapisuje wszystkie konta z registry do MongoDB"""
    try:
        accounts = registry.get_all_accounts()
        mongo_repo.save_all(accounts)
        return jsonify({
            "message": f"Successfully saved {len(accounts)} accounts to database"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/accounts/load", methods=['POST'])
def load_accounts():
    """Ładuje wszystkie konta z MongoDB do registry"""
    try:
        # Czyścimy obecne konta przed załadowaniem
        registry._accounts = []
        
        # Ładujemy z bazy
        accounts = mongo_repo.load_all()
        
        # Dodajemy do registry
        for account in accounts:
            registry.add_account(account)
        
        return jsonify({
            "message": f"Successfully loaded {len(accounts)} accounts from database"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)