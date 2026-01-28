from src.account_registry import AccountRegistry
from src.personal_account import PersonalAccount
import pytest


class TestAccountRegistry:
    """Testy dla AccountRegistry z użyciem fixtures i parametryzacji"""

    @pytest.fixture
    def registry(self):
        """Fixture: Pusty rejestr kont"""
        return AccountRegistry()

    @pytest.fixture
    def account1(self):
        """Fixture: Pierwsze konto testowe"""
        return PersonalAccount("John", "Doe", "89092909876")

    @pytest.fixture
    def account2(self):
        """Fixture: Drugie konto testowe"""
        return PersonalAccount("Jane", "Doe", "89092909877")

    @pytest.fixture
    def registry_with_accounts(self, registry, account1, account2):
        """Fixture: Registry z 2 kontami"""
        registry.add_account(account1)
        registry.add_account(account2)
        return registry

    def test_add_and_get_account(self, registry: AccountRegistry, account1):
        """Test dodawania i pobierania konta"""
        registry.add_account(account1)
        retrieved_account = registry.get_account_by_pesel("89092909876")
        assert retrieved_account == account1

    @pytest.mark.parametrize("pesel", [
        "00000000000",
        "11111111111",
        "99999999999",
    ])
    def test_get_account_not_found(self, registry: AccountRegistry, pesel):
        """Test wyszukiwania nieistniejącego konta - parametryzacja"""
        retrieved_account = registry.get_account_by_pesel(pesel)
        assert retrieved_account is None

    def test_get_all_accounts(self, registry_with_accounts, account1, account2):
        """Test pobierania wszystkich kont"""
        all_accounts = registry_with_accounts.get_all_accounts()
        assert all_accounts == [account1, account2]

    def test_get_account_count(self, registry_with_accounts):
        """Test liczenia kont w rejestrze"""
        assert registry_with_accounts.get_account_count() == 2

    def test_get_account_count_empty_registry(self, registry):
        """Test liczenia kont w pustym rejestrze"""
        assert registry.get_account_count() == 0

    def test_get_account_by_pesel_from_registry(self, registry_with_accounts, account1):
        """Test pobierania konkretnego konta po PESEL z registry"""
        retrieved = registry_with_accounts.get_account_by_pesel("89092909876")
        assert retrieved == account1
        assert retrieved.first_name == "John"

    def test_account_with_pesel_exists_true(self, registry, account1):
        """Test: sprawdzenie czy PESEL istnieje - pozytywnie"""
        registry.add_account(account1)
        assert registry.account_with_pesel_exists("89092909876") is True

    def test_account_with_pesel_exists_false(self, registry):
        """Test: sprawdzenie czy PESEL istnieje - negatywnie"""
        assert registry.account_with_pesel_exists("99999999999") is False

