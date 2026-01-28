import pytest
from unittest.mock import patch, MagicMock
from src.company_account import CompanyAccount


@pytest.fixture
def mock_mf_api():
    """Fixture: Mock API Ministerstwa Finansów - statusVat: Czynny"""
    with patch('src.company_account.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": {"statusVat": "Czynny", "nip": "1234567890"}
            }
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response
        yield mock_get


class TestCompanyAccountLoan:

    @pytest.fixture
    def company_account(self, mock_mf_api):
        return CompanyAccount("TechCorp", "1234567890")
    
    @pytest.fixture
    def account_with_zus_payment(self, mock_mf_api):
        account = CompanyAccount("TechCorp", "1234567890")
        account.balance = 10000.0
        account.outgoing_transfer(1775.0) # wpłata do zus
        return account
    
    @pytest.mark.parametrize("initial_balance,loan_amount", [
        (5000.0, 2000.0), # balance 5000 >= 2* 2000
        (10000.0, 4000.0),
        (6000.0, 3000.0),
    ])
    def test_loan_approved_sufficient_balance_and_zus(
        self, account_with_zus_payment, initial_balance, loan_amount
    ):
        #kredy przyznany: wystarczające saldo + wplata zus
        account_with_zus_payment.balance = initial_balance
        initial_balance_before = account_with_zus_payment.balance

        result = account_with_zus_payment.take_loan(loan_amount)
        assert result is True
        assert account_with_zus_payment.balance == initial_balance_before + loan_amount

    @pytest.mark.parametrize("balance,loan_amount", [
        (3000.0, 2000.0),
        (7000.0, 4000.0),
        (1000.0, 1000.0)
    ])
    def test_loan_rejected_insufficient_balance(
        self, account_with_zus_payment, balance, loan_amount
    ):
        # kredyt odrzucony, saldo < 2*loan
        account_with_zus_payment.balance = balance

        result = account_with_zus_payment.take_loan(loan_amount)

        assert result is False
        assert account_with_zus_payment.balance == balance # bez zmian


    @pytest.mark.parametrize("loan_amount", [1000.0, 2000.0, 5000.0])
    def test_loan_rejected_no_zus_payment(self, company_account, loan_amount):
        # kredyt odrzucony: brak wplaty do zus
        company_account.balance = 10000.0

        result = company_account.take_loan(loan_amount)

        assert result is False
        assert company_account.balance == 10000.0 # bez zmian


    
    #oba warunki niespelnione
    def test_loan_rejected_both_conditions_fail(self, company_account):
        company_account.balance = 2000.0

        result = company_account.take_loan(1500.0)

        assert result is False
        assert company_account.balance == 2000.0

    def test_loan_zus_payment_exact_amount(self, mock_mf_api):
        #Warunek ZUS musi być dokładnie -1775
        account = CompanyAccount("TechCorp", "1234567890")
        account.balance = 10000.0
        account.outgoing_transfer(1774.0)  # Blisko, ale nie -1775
        
        result = account.take_loan(2000.0)
        
        assert result is False  # Nie ma dokładnie -1775