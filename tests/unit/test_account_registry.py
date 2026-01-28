from src.account_registry import AccountRegistry
from src.personal_account import PersonalAccount
import pytest


class TestAccountRegistry:
    """Testy dla AccountRegistry z użyciem fixtures i parametryzacji"""

    @pytest.fixture
    def registry(self):
        return AccountRegistry()

    @pytest.fixture
    def account1(self):
        return PersonalAccount("John", "Doe", "89092909876")

    @pytest.fixture
    def account2(self):
        return PersonalAccount("Jane", "Doe", "89092909877")

    @pytest.fixture
    def registry_with_accounts(self, registry, account1, account2):
        registry.add_account(account1)
        registry.add_account(account2)
        return registry

    def test_add_and_get_account(self, registry: AccountRegistry, account1):
        registry.add_account(account1)
        retrieved_account = registry.get_account_by_pesel("89092909876")
        assert retrieved_account == account1

    @pytest.mark.parametrize("pesel", [
        "00000000000",
        "11111111111",
        "99999999999",
    ])
    def test_get_account_not_found(self, registry: AccountRegistry, pesel):
        retrieved_account = registry.get_account_by_pesel(pesel)
        assert retrieved_account is None

    def test_get_all_accounts(self, registry_with_accounts, account1, account2):
        all_accounts = registry_with_accounts.get_all_accounts()
        assert all_accounts == [account1, account2]

    def test_get_account_count(self, registry_with_accounts):
        assert registry_with_accounts.get_account_count() == 2

    def test_get_account_count_empty_registry(self, registry):
        assert registry.get_account_count() == 0

    def test_get_account_by_pesel_from_registry(self, registry_with_accounts, account1):
        retrieved = registry_with_accounts.get_account_by_pesel("89092909876")
        assert retrieved == account1
        assert retrieved.first_name == "John"

    def test_account_with_pesel_exists_true(self, registry, account1):
        registry.add_account(account1)
        assert registry.account_with_pesel_exists("89092909876") is True

    def test_account_with_pesel_exists_false(self, registry):
        assert registry.account_with_pesel_exists("99999999999") is False

    def test_delete_account_success(self, registry, account1):
        registry.add_account(account1)
        assert registry.get_account_count() == 1
        result = registry.delete_account("89092909876")
        assert result is True
        assert registry.get_account_count() == 0

    def test_delete_account_not_found(self, registry):
        result = registry.delete_account("99999999999")
        assert result is False

    def test_delete_account_from_multiple(self, registry, account1, account2):
        """Test: Usuwanie pierwszego konta gdy są inne konta - pokrywa branch 25->24"""
        registry.add_account(account1)
        registry.add_account(account2)
        assert registry.get_account_count() == 2
        result = registry.delete_account("89092909876")
        assert result is True
        assert registry.get_account_count() == 1
        assert registry.get_account_by_pesel("89092909877") is not None

    def test_delete_account_second_in_list(self, registry, account1, account2):
        """Test: Usuwanie drugiego konta - wymusza iterację pętli"""
        registry.add_account(account1)
        registry.add_account(account2)
        result = registry.delete_account("89092909877")  # Usuń drugie konto
        assert result is True
        assert registry.get_account_count() == 1
        assert registry.get_account_by_pesel("89092909876") is not None

    #  BRAKUJĄCE GAŁĘZIE 

    def test_get_account_by_pesel_not_matching_existing_accounts(self, registry, account1, account2):
        """Registry ma konta, ale żaden PESEL nie pasuje"""
        registry.add_account(account1)
        registry.add_account(account2)

        result = registry.get_account_by_pesel("00000000000")
        assert result is None

    def test_account_with_pesel_exists_false_when_other_accounts_exist(self, registry, account1):
        """Registry nie jest pusty, ale PESEL nie istnieje"""
        registry.add_account(account1)

        result = registry.account_with_pesel_exists("99999999999")
        assert result is False


    def test_delete_account_when_multiple_accounts_exist(self, registry, account1, account2):
        """Usuwanie drugiego konta z listy (pętla przechodzi dalej)"""
        registry.add_account(account1)
        registry.add_account(account2)

        result = registry.delete_account("89092909877")  # account2
        assert result is True
        assert registry.get_account_count() == 1
        assert registry.get_account_by_pesel("89092909877") is None
        assert registry.get_account_by_pesel("89092909876") == account1
