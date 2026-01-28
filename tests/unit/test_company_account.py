import pytest
from unittest.mock import patch, MagicMock
from src.company_account import CompanyAccount


class TestCompanyAccount:

    @patch('src.company_account.requests.get')
    def test_company_account_creation_valid_nip(self, mock_get):
        """Test: Tworzenie konta z ważnym NIPem (Feature 18 - mock API MF)"""
        # Mock odpowiedzi MF API - prawdziwy format z subject.statusVat: Czynny
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Czynny",
                    "nip": "1234567890"
                }
            }
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response
        
        account = CompanyAccount("Firma", "1234567890")
        assert account.company_name == "Firma"
        assert account.nip == "1234567890"
        
        # Sprawdź że API został wysłany
        mock_get.assert_called_once()

    @patch('src.company_account.requests.get')
    def test_company_account_invalid_nip_inactive(self, mock_get):
        """Test: Tworzenie konta z NIPem nieaktywnym (statusVat != Czynny)"""
        # Mock odpowiedzi MF API - subject.statusVat: Wznowiony (nie Czynny)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Wznowiony",  # Nie "Czynny"
                    "nip": "1234567890"
                }
            }
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Wznowiony"}}}'
        mock_get.return_value = mock_response
        
        # Powinno rzucić ValueError
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("Firma", "1234567890")

    @patch('src.company_account.requests.get')
    def test_company_account_invalid_nip_not_found(self, mock_get):
        """Test: Tworzenie konta z NIPem który nie istnieje w MF"""
        # Mock odpowiedzi MF API - subject: null (NIP nie istnieje)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": None  # NIP nie istnieje w bazie
            }
        }
        mock_response.text = '{"result": {"subject": null}}'
        mock_get.return_value = mock_response
        
        # Powinno rzucić ValueError
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("Firma", "1234567890")

    def test_company_account_short_nip_no_api_call(self):
        """Test: NIP ze złą długością - nie wysyłamy requestu do API"""
        account = CompanyAccount("Firma", "123456789")
        assert account.company_name == "Firma"
        assert account.nip == "Invalid"
        # Nie rzuca błędu, bo NIP za krótki

    @patch('src.company_account.requests.get')
    def test_company_account_api_timeout(self, mock_get):
        """Test: Timeout przy połączeniu z API MF"""
        mock_get.side_effect = Exception("Connection timeout")
        
        # Powinno rzucić ValueError
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("Firma", "1234567890")

