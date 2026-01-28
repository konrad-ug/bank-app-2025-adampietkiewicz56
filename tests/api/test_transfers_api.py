import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/api/accounts"


class TestTransfersAPI:
    """Testy integracyjne API dla przelewów (Feature 17)"""

    @pytest.fixture
    def account_with_balance(self):
        """Fixture: Konto z pieniędzmi do przelewów"""
        pesel = "12121212121"
        
        # Stwórz konto
        requests.post(BASE_URL, json={
            "name": "Rich",
            "surname": "Guy",
            "pesel": pesel
        })
        
        # Dodaj pieniądze
        requests.post(f"{BASE_URL}/{pesel}/transfer", json={
            "amount": 1000,
            "type": "incoming"
        })
        
        return pesel

    @pytest.fixture
    def empty_account(self):
        """Fixture: Puste konto bez pieniędzy"""
        pesel = "13131313131"
        
        requests.post(BASE_URL, json={
            "name": "Poor",
            "surname": "Guy",
            "pesel": pesel
        })
        
        return pesel

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Fixture: Czyści wszystkie konta po testach"""
        yield
        try:
            response = requests.get(BASE_URL, timeout=2)
            if response.status_code == 200:
                accounts = response.json()
                for account in accounts:
                    requests.delete(f"{BASE_URL}/{account['pesel']}", timeout=2)
        except requests.exceptions.RequestException:
            pass

    # ========== INCOMING TRANSFER TESTS ==========

    def test_transfer_incoming_success(self, account_with_balance):
        """Test: Przelew przychodzący - sukces"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 500, "type": "incoming"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Zlecenie przyjęto do realizacji"
        
        # Sprawdź saldo
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 1500  # 1000 + 500

    def test_transfer_incoming_multiple(self, empty_account):
        """Test: Wiele przelewów przychodzących"""
        pesel = empty_account
        
        # Pierwszy przelew
        response1 = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 300, "type": "incoming"}
        )
        assert response1.status_code == 200
        
        # Drugi przelew
        response2 = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 200, "type": "incoming"}
        )
        assert response2.status_code == 200
        
        # Sprawdź ostateczne saldo
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 500  # 300 + 200

    # ========== OUTGOING TRANSFER TESTS ==========

    def test_transfer_outgoing_success(self, account_with_balance):
        """Test: Przelew wychodzący - sukces"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 300, "type": "outgoing"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Zlecenie przyjęto do realizacji"
        
        # Sprawdź saldo
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 700  # 1000 - 300

    def test_transfer_outgoing_insufficient_funds(self, empty_account):
        """Test: Przelew wychodzący - brak środków (422)"""
        pesel = empty_account
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 500, "type": "outgoing"}
        )
        
        assert response.status_code == 422  # ← Unprocessable Entity
        assert "Insufficient funds" in response.json()["error"]
        
        # Sprawdź że saldo się nie zmieniło
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 0  # Bez zmian

    def test_transfer_outgoing_exact_balance(self, account_with_balance):
        """Test: Przelew dokładnie całego salda"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 1000, "type": "outgoing"}
        )
        
        assert response.status_code == 200
        
        # Sprawdź że saldo == 0
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 0

    # ========== EXPRESS TRANSFER TESTS ==========

    def test_transfer_express_success(self, account_with_balance):
        """Test: Przelew express - sukces"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 100, "type": "express"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Zlecenie przyjęto do realizacji"
        
        # Sprawdź saldo - powinno być 1000 - 100 - 1 (opłata)
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 899  # 1000 - 100 - 1

    def test_transfer_express_insufficient_funds(self, empty_account):
        """Test: Express transfer - brak środków (422)"""
        pesel = empty_account
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 50, "type": "express"}
        )
        
        assert response.status_code == 422
        assert "Insufficient funds" in response.json()["error"]

    # ========== ERROR TESTS ==========

    def test_transfer_account_not_found(self):
        """Test: Przelew - konto nie istnieje (404)"""
        response = requests.post(
            f"{BASE_URL}/99999999999/transfer",
            json={"amount": 100, "type": "incoming"}
        )
        
        assert response.status_code == 404
        assert "Account not found" in response.json()["error"]

    def test_transfer_invalid_type(self, account_with_balance):
        """Test: Przelew - nieznany typ (400)"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 100, "type": "invalid"}
        )
        
        assert response.status_code == 400  # Bad Request
        assert "Invalid transfer type" in response.json()["error"]

    @pytest.mark.parametrize("invalid_type", ["unknown", "fast", "urgent", "xxx"])
    def test_transfer_invalid_types_parametrized(self, account_with_balance, invalid_type):
        """Test: Wiele nieprawidłowych typów - parametryzacja"""
        pesel = account_with_balance
        
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 100, "type": invalid_type}
        )
        
        assert response.status_code == 400

    # ========== FLOW TESTS ==========

    def test_transfer_flow_multiple_operations(self, empty_account):
        """Test: Flow - kilka operacji na jednym koncie"""
        pesel = empty_account
        
        # 1. Przelew przychodzący 1000
        response1 = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 1000, "type": "incoming"}
        )
        assert response1.status_code == 200
        
        # 2. Przelew wychodzący 300
        response2 = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 300, "type": "outgoing"}
        )
        assert response2.status_code == 200
        
        # 3. Przelew express 100 (+ 1 opłata)
        response3 = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 100, "type": "express"}
        )
        assert response3.status_code == 200
        
        # 4. Sprawdzenie salda: 1000 - 300 - 100 - 1 = 599
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 599

    def test_transfer_outgoing_after_incoming(self, empty_account):
        """Test: Przelew wychodzący po przychodzącym"""
        pesel = empty_account
        
        # Dodaj pieniądze
        requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 500, "type": "incoming"}
        )
        
        # Wyślij pieniądze
        response = requests.post(
            f"{BASE_URL}/{pesel}/transfer",
            json={"amount": 200, "type": "outgoing"}
        )
        
        assert response.status_code == 200
        
        # Sprawdź saldo: 500 - 200 = 300
        get_response = requests.get(f"{BASE_URL}/{pesel}")
        balance = get_response.json()["balance"]
        assert balance == 300
