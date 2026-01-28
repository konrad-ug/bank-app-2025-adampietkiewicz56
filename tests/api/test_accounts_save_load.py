import requests
import pytest
import time


BASE_URL = "http://localhost:5000"


class TestAccountsSaveLoad:
    """Testy API dla zapisywania i ładowania kont z MongoDB"""
    
    def setup_method(self):
        """Setup - czyszczenie registry przed każdym testem"""
        # Usuń wszystkie konta
        response = requests.get(f"{BASE_URL}/api/accounts")
        if response.status_code == 200:
            accounts = response.json()
            for account in accounts:
                requests.delete(f"{BASE_URL}/api/accounts/{account['pesel']}")
    
    def test_save_accounts_to_database(self):
        """Test: POST /api/accounts/save zapisuje konta do MongoDB"""
        # Utwórz kilka kont
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "John",
            "surname": "Doe",
            "pesel": "90010112345"
        })
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Jane",
            "surname": "Smith",
            "pesel": "85020223456"
        })
        
        # Wykonaj przelew na pierwsze konto
        requests.post(f"{BASE_URL}/api/accounts/90010112345/transfer", json={
            "amount": 100,
            "type": "incoming"
        })
        
        # Zapisz do bazy
        response = requests.post(f"{BASE_URL}/api/accounts/save")
        
        assert response.status_code == 200
        data = response.json()
        assert "Successfully saved" in data["message"]
        assert "2 accounts" in data["message"]
    
    def test_load_accounts_from_database(self):
        """Test: POST /api/accounts/load ładuje konta z MongoDB"""
        # Utwórz konto i zapisz do bazy
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Test",
            "surname": "User",
            "pesel": "92030334567"
        })
        requests.post(f"{BASE_URL}/api/accounts/92030334567/transfer", json={
            "amount": 500,
            "type": "incoming"
        })
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Usuń wszystkie konta z registry
        requests.delete(f"{BASE_URL}/api/accounts/92030334567")
        
        # Sprawdź że registry jest puste
        response = requests.get(f"{BASE_URL}/api/accounts/count")
        assert response.json()["count"] == 0
        
        # Załaduj z bazy
        response = requests.post(f"{BASE_URL}/api/accounts/load")
        
        assert response.status_code == 200
        data = response.json()
        assert "Successfully loaded" in data["message"]
        assert "1 accounts" in data["message"]
        
        # Sprawdź czy konto jest w registry
        response = requests.get(f"{BASE_URL}/api/accounts/92030334567")
        assert response.status_code == 200
        account = response.json()
        assert account["name"] == "Test"
        assert account["surname"] == "User"
        assert account["balance"] == 500
    
    def test_load_clears_existing_accounts(self):
        """Test: load() czyści obecne konta przed załadowaniem"""
        # Utwórz konto A i zapisz do bazy
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Alice",
            "surname": "Wonder",
            "pesel": "88040445678"
        })
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Usuń konto A i utwórz konto B
        requests.delete(f"{BASE_URL}/api/accounts/88040445678")
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Bob",
            "surname": "Builder",
            "pesel": "91050556789"
        })
        
        # Sprawdź że w registry jest tylko Bob
        response = requests.get(f"{BASE_URL}/api/accounts")
        accounts = response.json()
        assert len(accounts) == 1
        assert accounts[0]["pesel"] == "91050556789"
        
        # Załaduj z bazy (powinno być tylko Alice)
        requests.post(f"{BASE_URL}/api/accounts/load")
        
        # Sprawdź że w registry jest tylko Alice
        response = requests.get(f"{BASE_URL}/api/accounts")
        accounts = response.json()
        assert len(accounts) == 1
        assert accounts[0]["pesel"] == "88040445678"
        assert accounts[0]["name"] == "Alice"
    
    def test_save_and_load_preserves_balance_and_history(self):
        """Test: save/load zachowuje balance i history"""
        # Utwórz konto i wykonaj kilka operacji
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Charlie",
            "surname": "Brown",
            "pesel": "87060667890"
        })
        requests.post(f"{BASE_URL}/api/accounts/87060667890/transfer", json={
            "amount": 200,
            "type": "incoming"
        })
        requests.post(f"{BASE_URL}/api/accounts/87060667890/transfer", json={
            "amount": 50,
            "type": "outgoing"
        })
        requests.post(f"{BASE_URL}/api/accounts/87060667890/transfer", json={
            "amount": 100,
            "type": "incoming"
        })
        
        # Sprawdź balans przed zapisem
        response = requests.get(f"{BASE_URL}/api/accounts/87060667890")
        assert response.json()["balance"] == 250
        
        # Zapisz do bazy
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Usuń z registry
        requests.delete(f"{BASE_URL}/api/accounts/87060667890")
        
        # Załaduj z bazy
        requests.post(f"{BASE_URL}/api/accounts/load")
        
        # Sprawdź że balance się zgadza
        response = requests.get(f"{BASE_URL}/api/accounts/87060667890")
        assert response.status_code == 200
        account = response.json()
        assert account["balance"] == 250
    
    def test_save_overwrites_previous_data(self):
        """Test: save() nadpisuje poprzednie dane (delete_many)"""
        # Utwórz konto A i zapisz
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Dave",
            "surname": "Davis",
            "pesel": "89070778901"
        })
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Usuń konto A i utwórz konto B
        requests.delete(f"{BASE_URL}/api/accounts/89070778901")
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Eve",
            "surname": "Evans",
            "pesel": "90080889012"
        })
        
        # Zapisz ponownie
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Wyczyść registry i załaduj z bazy
        requests.delete(f"{BASE_URL}/api/accounts/90080889012")
        requests.post(f"{BASE_URL}/api/accounts/load")
        
        # Sprawdź że w bazie jest tylko Eve (Dave został nadpisany)
        response = requests.get(f"{BASE_URL}/api/accounts")
        accounts = response.json()
        assert len(accounts) == 1
        assert accounts[0]["pesel"] == "90080889012"
        assert accounts[0]["name"] == "Eve"
    
    def test_save_empty_registry(self):
        """Test: save() działa dla pustego registry"""
        # Upewnij się że registry jest puste
        response = requests.get(f"{BASE_URL}/api/accounts")
        for account in response.json():
            requests.delete(f"{BASE_URL}/api/accounts/{account['pesel']}")
        
        # Zapisz puste registry
        response = requests.post(f"{BASE_URL}/api/accounts/save")
        
        assert response.status_code == 200
        assert "0 accounts" in response.json()["message"]
    
    def test_load_from_empty_database(self):
        """Test: load() działa dla pustej bazy"""
        # Zapisz puste registry (wyczyści bazę)
        requests.post(f"{BASE_URL}/api/accounts/save")
        
        # Utwórz konto lokalnie
        requests.post(f"{BASE_URL}/api/accounts", json={
            "name": "Frank",
            "surname": "Foster",
            "pesel": "93090990123"
        })
        
        # Załaduj z pustej bazy
        response = requests.post(f"{BASE_URL}/api/accounts/load")
        
        assert response.status_code == 200
        assert "0 accounts" in response.json()["message"]
        
        # Sprawdź że registry jest puste
        response = requests.get(f"{BASE_URL}/api/accounts/count")
        assert response.json()["count"] == 0
