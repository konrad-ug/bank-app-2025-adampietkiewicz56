import pytest
from src.personal_account import PersonalAccount

@pytest.fixture
def personal_account():
    """Fixture: Czyste konto osobiste."""
    return PersonalAccount("Jan", "Kowalski", "12345678901")

@pytest.fixture
def account_with_three_deposits(personal_account):
    """Fixture: Konto z 3 wpłatami."""
    personal_account.incoming_transfer(100)
    personal_account.incoming_transfer(200)
    personal_account.incoming_transfer(150)
    return personal_account

@pytest.fixture
def account_with_five_transactions(personal_account):
    """Fixture: Konto z 5 transakcjami (mieszane)."""
    personal_account.incoming_transfer(200)
    personal_account.outgoing_transfer(50)
    personal_account.incoming_transfer(300)
    personal_account.outgoing_transfer(100)
    personal_account.incoming_transfer(150)
    return personal_account

# Parametryzacja dla pozytywnych scenariuszy
@pytest.mark.parametrize("loan_amount,expected_balance", [
    (100, 550),  # 450 + 100
    (300, 750),  # 450 + 300
    (50, 500),   # 450 + 50
])
def test_loan_approved_last_three_deposits(account_with_three_deposits, loan_amount, expected_balance):
    """Kredyt przyznany: ostatnie 3 to wpłaty."""
    result = account_with_three_deposits.submit_for_loan(loan_amount)
    assert result is True
    assert account_with_three_deposits.balance == expected_balance

@pytest.mark.parametrize("loan_amount", [100, 200, 400])
def test_loan_approved_sum_of_last_five(account_with_five_transactions, loan_amount):
    """Kredyt przyznany: suma ostatnich 5 > kwota kredytu."""
    initial_balance = account_with_five_transactions.balance
    result = account_with_five_transactions.submit_for_loan(loan_amount)
    assert result is True
    assert account_with_five_transactions.balance == initial_balance + loan_amount

# Parametryzacja dla negatywnych scenariuszy
@pytest.mark.parametrize("transactions,loan_amount", [
    ([100, -50, -30], 100),  # ostatnie 3 nie są wpłatami
    ([100, 50], 500),        # za mało transakcji
    ([100, 50, 20, -10, 30], 200),  # suma ostatnich 5 (100+50+20-10+30=190) < 200
])
def test_loan_rejected(personal_account, transactions, loan_amount):
    """Kredyt odrzucony: warunki nie spełnione."""
    for amount in transactions:
        if amount > 0:
            personal_account.incoming_transfer(amount)
        else:
            personal_account.outgoing_transfer(abs(amount))
    
    initial_balance = personal_account.balance
    result = personal_account.submit_for_loan(loan_amount)
    assert result is False
    assert personal_account.balance == initial_balance