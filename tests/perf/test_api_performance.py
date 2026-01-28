"""Performance tests dla API - sprawdzenie czasu odpowiedzi"""
import requests
import time
import pytest


BASE_URL = "http://127.0.0.1:5000/api"


class TestAPIPerformance:
    """Testy wydajnościowe API - każdy request < 0.5s"""

    def test_create_and_delete_account_100_times(self):
        """
        Test: Tworzenie i usuwanie konta 100 razy
        Każda operacja (create + delete) musi być krótsza niż 0.5s
        """
        for i in range(100):
            pesel = f"1234567{i:04d}"  # Generuj unikalne PESEL
            
            # CREATE - sprawdź czas odpowiedzi
            start_time = time.time()
            create_response = requests.post(
                f"{BASE_URL}/accounts",
                json={
                    "name": f"Test{i}",
                    "surname": f"User{i}",
                    "pesel": pesel
                },
                timeout=0.5  # Timeout 0.5s
            )
            create_duration = time.time() - start_time
            
            # Sprawdź poprawność
            assert create_response.status_code == 201, f"Create failed at iteration {i}"
            assert create_duration < 0.5, f"Create took {create_duration}s (> 0.5s) at iteration {i}"
            
            # DELETE - sprawdź czas odpowiedzi
            start_time = time.time()
            delete_response = requests.delete(
                f"{BASE_URL}/accounts/{pesel}",
                timeout=0.5  # Timeout 0.5s
            )
            delete_duration = time.time() - start_time
            
            # Sprawdź poprawność
            assert delete_response.status_code == 200, f"Delete failed at iteration {i}"
            assert delete_duration < 0.5, f"Delete took {delete_duration}s (> 0.5s) at iteration {i}"

    def test_create_account_and_100_incoming_transfers(self):
        """
        Test: Stworzenie konta i 100 przelewów przychodzących
        Każdy request musi być krótszy niż 0.5s
        Weryfikacja końcowego salda
        """
        pesel = "99988877766"
        transfer_amount = 100
        expected_balance = transfer_amount * 100  # 100 * 100 = 10000
        
        # CREATE konto
        start_time = time.time()
        create_response = requests.post(
            f"{BASE_URL}/accounts",
            json={
                "name": "Performance",
                "surname": "Test",
                "pesel": pesel
            },
            timeout=0.5
        )
        create_duration = time.time() - start_time
        
        assert create_response.status_code == 201, "Account creation failed"
        assert create_duration < 0.5, f"Create took {create_duration}s (> 0.5s)"
        
        # 100 INCOMING TRANSFERS
        for i in range(100):
            start_time = time.time()
            transfer_response = requests.post(
                f"{BASE_URL}/accounts/{pesel}/transfer",
                json={
                    "type": "incoming",
                    "amount": transfer_amount
                },
                timeout=0.5
            )
            transfer_duration = time.time() - start_time
            
            # Sprawdź poprawność
            assert transfer_response.status_code == 200, f"Transfer {i} failed"
            assert transfer_duration < 0.5, f"Transfer {i} took {transfer_duration}s (> 0.5s)"
        
        # VERIFY FINAL BALANCE
        get_response = requests.get(f"{BASE_URL}/accounts/{pesel}", timeout=0.5)
        assert get_response.status_code == 200, "Get account failed"
        
        account_data = get_response.json()
        final_balance = account_data.get("balance", 0)
        
        assert final_balance == expected_balance, (
            f"Expected balance {expected_balance}, got {final_balance}"
        )
        
        # CLEANUP - usuń konto
        requests.delete(f"{BASE_URL}/accounts/{pesel}", timeout=0.5)

    @pytest.mark.optional
    def test_create_1000_accounts_then_delete_all(self):
        """
        Test opcjonalny: Stwórz 1000 kont, potem wszystkie usuń
        
        Różnica vs create-delete w pętli:
        - Ten test sprawdza stabilność przy dużej liczbie rekordów w pamięci
        - Testuje czy lista kont nie spowalnia operacji przy większej bazie
        - Weryfikuje brak memory leaks przy wielu obiektach
        - Create-delete w pętli testuje pojedyncze operacje, ten test sprawdza skalowanie
        """
        pesels = []
        
        # PHASE 1: CREATE 1000 accounts
        for i in range(1000):
            pesel = f"8888888{i:04d}"
            pesels.append(pesel)
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/accounts",
                json={
                    "name": f"Batch{i}",
                    "surname": f"User{i}",
                    "pesel": pesel
                },
                timeout=0.5
            )
            duration = time.time() - start_time
            
            assert response.status_code == 201, f"Create failed at {i}"
            assert duration < 0.5, f"Create {i} took {duration}s (> 0.5s)"
        
        # PHASE 2: DELETE all 1000 accounts
        for i, pesel in enumerate(pesels):
            start_time = time.time()
            response = requests.delete(
                f"{BASE_URL}/accounts/{pesel}",
                timeout=0.5
            )
            duration = time.time() - start_time
            
            assert response.status_code == 200, f"Delete failed at {i}"
            assert duration < 0.5, f"Delete {i} took {duration}s (> 0.5s)"
