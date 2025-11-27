from src.account_registry import AccountRegistry
from src.personal_account import PersonalAccount
import pytest


class TestAccountRegistry:
    @pytest.fixture
    def registry(self):
        return AccountRegistry()

    def test_add_and_get_account(self, registry: AccountRegistry):
        account = PersonalAccount("John", "Doe", "89092909876")
        registry.add_account(account)
        retrieved_account = registry.get_account_by_pesel("89092909876")
        assert retrieved_account == account
    
    def test_get_account_not_found(self, registry: AccountRegistry):
        retrieved_account = registry.get_account_by_pesel("00000000000")
        assert retrieved_account is None

    def test_get_all_accounts(self, registry: AccountRegistry):
        account1 = PersonalAccount("John", "Doe", "89092909876")
        account2 = PersonalAccount("Jane", "Doe", "89092909877")
        registry.add_account(account1)
        registry.add_account(account2)
        all_accounts = registry.get_all_accounts()
        assert all_accounts == [account1, account2]