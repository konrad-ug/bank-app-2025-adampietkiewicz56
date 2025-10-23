from src.account import Account

class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe", "02040722492", 0)
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.pesel == "02040722492"
        assert account.balance == 0

    def test_valid_pesel(self):  
        acc = Account("Anna", "Nowak", "90010112345")
        assert acc.pesel == "90010112345"

    def test_invalid_pesel_short(self): 
        acc = Account("Piotr", "Kowalski", "1234567890")
        assert acc.pesel == "Invalid"

    def test_invalid_pesel_long(self):
        acc = Account("Ala", "Makota", "123456789012")
        assert acc.pesel == "Invalid"

    def test_account_without_promo_code(self):
        acc = Account("Adam", "Nowak", "90010112345")
        assert acc.balance == 0

    def test_account_with_valid_promo_code(self):
        acc = Account("Ewa", "Nowak", "90010112345", promo_code="PROM_ABC")
        assert acc.balance == 50

    def test_account_with_invalid_promo_code_prefix(self):
        acc = Account("Ewa", "Nowak", "90010112345", promo_code="ABC_PROM")
        assert acc.balance == 0

    def test_account_with_invalid_promo_code_format(self):
        acc = Account("Ewa", "Nowak", "90010112345", promo_code="PROM-ABC")
        assert acc.balance == 0

    def test_account_with_none_as_promo_code(self):
        acc = Account("Ewa", "Nowak", "90010112345", promo_code=None)
        assert acc.balance == 0