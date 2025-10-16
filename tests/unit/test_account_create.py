from src.account import Account


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe", "02040722492", 0)
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.pesel == "02040722492"
        assert account.balance == 0
