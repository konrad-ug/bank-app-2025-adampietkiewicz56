import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/api/accounts"


class TestAccountCRUD:
    """Testy integracyjne API dla CRUD kont osobistych"""

    @pytest.fixture
    def base_url(self):
        """Fixture: Base URL for API"""
        return BASE_URL

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Fixture: Czyści wszystkie konta przed każdym testem"""
        yield
        # Po teście usuń wszystkie konta
        try:
            response = requests.get(BASE_URL, timeout=2)
            if response.status_code == 200:
                accounts = response.json()
                for account in accounts:
                    requests.delete(f"{BASE_URL}/{account['pesel']}", timeout=2)
        except requests.exceptions.RequestException:
            pass  # Serwer może nie działać podczas testów

    def test_create_account(self, base_url):
        """Test: POST /api/accounts - tworzenie konta"""
        payload = {
            "name": "James",
            "surname": "Hetfield",
            "pesel": "89092909825"
        }
        response = requests.post(base_url, json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Account created"

    def test_get_all_accounts(self, base_url):
        """Test: GET /api/accounts - pobierz wszystkie konta"""
        # Stwórz konto
        requests.post(base_url, json={"name": "John", "surname": "Doe", "pesel": "12345678901"})

        # Pobierz wszystkie
        response = requests.get(base_url)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_all_accounts_empty(self, base_url):
        """Test: GET /api/accounts - pusta lista gdy brak kont"""
        response = requests.get(base_url)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_account_count(self, base_url):
        """Test: GET /api/accounts/count"""
        # Dodaj 2 konta
        requests.post(base_url, json={"name": "John", "surname": "Doe", "pesel": "11111111111"})
        requests.post(base_url, json={"name": "Jane", "surname": "Doe", "pesel": "22222222222"})

        # Sprawdź count
        response = requests.get(f"{base_url}/count")
        assert response.status_code == 200
        assert response.json()["count"] >= 2

    def test_get_account_by_pesel(self, base_url):
        """Test: GET /api/accounts/<pesel> - znalezione"""
        pesel = "89092909825"
        requests.post(base_url, json={"name": "James", "surname": "Hetfield", "pesel": pesel})

        response = requests.get(f"{base_url}/{pesel}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "James"
        assert data["surname"] == "Hetfield"
        assert data["pesel"] == pesel
        assert "balance" in data

    def test_get_account_by_pesel_not_found(self, base_url):
        """Test: GET /api/accounts/<pesel> - 404"""
        response = requests.get(f"{base_url}/99999999999")
        assert response.status_code == 404
        assert "error" in response.json()

    @pytest.mark.parametrize("pesel,expected_status", [
        ("00000000000", 404),
        ("11111111111", 404),
    ])
    def test_get_nonexistent_accounts(self, base_url, pesel, expected_status):
        """Test: GET /api/accounts/<pesel> - parametryzacja dla nieistniejących kont"""
        response = requests.get(f"{base_url}/{pesel}")
        assert response.status_code == expected_status

    def test_update_account_name_only(self, base_url):
        """Test: PATCH /api/accounts/<pesel> - update tylko name"""
        pesel = "33333333333"
        requests.post(base_url, json={"name": "John", "surname": "Doe", "pesel": pesel})

        # Update tylko name
        update_payload = {"name": "Johnny"}
        response = requests.patch(f"{base_url}/{pesel}", json=update_payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Account updated"

        # Sprawdź czy się zmieniło
        get_response = requests.get(f"{base_url}/{pesel}")
        assert get_response.json()["name"] == "Johnny"
        assert get_response.json()["surname"] == "Doe"  # bez zmian

    def test_update_account_surname_only(self, base_url):
        """Test: PATCH /api/accounts/<pesel> - update tylko surname"""
        pesel = "44444444444"
        requests.post(base_url, json={"name": "Jane", "surname": "Doe", "pesel": pesel})

        # Update tylko surname
        update_payload = {"surname": "Smith"}
        response = requests.patch(f"{base_url}/{pesel}", json=update_payload)
        assert response.status_code == 200

        # Sprawdź
        get_response = requests.get(f"{base_url}/{pesel}")
        assert get_response.json()["name"] == "Jane"  # bez zmian
        assert get_response.json()["surname"] == "Smith"

    def test_update_account_both_fields(self, base_url):
        """Test: PATCH /api/accounts/<pesel> - update name i surname"""
        pesel = "55555555555"
        requests.post(base_url, json={"name": "John", "surname": "Doe", "pesel": pesel})

        # Update oba pola
        update_payload = {"name": "Johnny", "surname": "Smith"}
        response = requests.patch(f"{base_url}/{pesel}", json=update_payload)
        assert response.status_code == 200

        # Sprawdź
        get_response = requests.get(f"{base_url}/{pesel}")
        assert get_response.json()["name"] == "Johnny"
        assert get_response.json()["surname"] == "Smith"

    def test_update_account_not_found(self, base_url):
        """Test: PATCH /api/accounts/<pesel> - 404"""
        response = requests.patch(f"{base_url}/99999999999", json={"name": "Test"})
        assert response.status_code == 404

    def test_delete_account(self, base_url):
        """Test: DELETE /api/accounts/<pesel>"""
        pesel = "66666666666"
        requests.post(base_url, json={"name": "John", "surname": "Doe", "pesel": pesel})

        # Delete
        response = requests.delete(f"{base_url}/{pesel}")
        assert response.status_code == 200
        assert response.json()["message"] == "Account deleted"

        # Sprawdź czy usunięte
        get_response = requests.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 404

    def test_delete_account_not_found(self, base_url):
        """Test: DELETE /api/accounts/<pesel> - 404"""
        response = requests.delete(f"{base_url}/99999999999")
        assert response.status_code == 404

    def test_full_crud_flow(self, base_url):
        """Test: Pełny flow CRUD - Create, Read, Update, Delete"""
        pesel = "77777777777"

        # 1. CREATE
        create_response = requests.post(base_url, json={
            "name": "Alice",
            "surname": "Wonder",
            "pesel": pesel
        })
        assert create_response.status_code == 201

        # 2. READ
        get_response = requests.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Alice"

        # 3. UPDATE
        update_response = requests.patch(f"{base_url}/{pesel}", json={"name": "Alicia"})
        assert update_response.status_code == 200

        # 4. READ again
        get_response2 = requests.get(f"{base_url}/{pesel}")
        assert get_response2.json()["name"] == "Alicia"

        # 5. DELETE
        delete_response = requests.delete(f"{base_url}/{pesel}")
        assert delete_response.status_code == 200

        # 6. READ after delete (404)
        get_response3 = requests.get(f"{base_url}/{pesel}")
        assert get_response3.status_code == 404
