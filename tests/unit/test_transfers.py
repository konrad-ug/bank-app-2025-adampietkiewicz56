from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount

class TestTransfers:

    def test_outgoing_transfer(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0

        account.outgoing_transfer(50.0)
        assert account.balance == 50.0

    def test_outgoing_transfer_exceeding_balance(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0

        account.outgoing_transfer(50.0)
        assert account.balance == 30.0

    def test_incoming_transfer_negative_amount(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0
        account.incoming_transfer(-20.0)
        assert account.balance == 30.0

    def test_incoming_transfer_correct_amount(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0
        account.incoming_transfer(20.0)
        assert account.balance == 50.0

    def test_incoming_transfer_correct_amount_company(self):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.incoming_transfer(20.0)
        assert account.balance == 120.0
