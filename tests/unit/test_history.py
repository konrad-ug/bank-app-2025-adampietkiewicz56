from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestHistory:
    def test_outgoing_personal_express(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.express_outgoing_pers(50.0)
        assert account.balance == 99.0
        assert account.history == [-50.0, -1.0]

    def test_outgoing_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.outgoing_transfer(50.0)
        assert account.balance == 100.0
        assert account.history == [-50.0]