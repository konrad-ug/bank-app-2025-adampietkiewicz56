import pytest
from unittest.mock import Mock, patch, MagicMock
from src.mongo_repository import MongoAccountsRepository
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestMongoAccountsRepository:
    """Unit testy dla MongoAccountsRepository z użyciem mocków"""
    
    def setup_method(self):
        """Setup przed każdym testem - utworzenie testowych kont"""
        self.account1 = PersonalAccount("John", "Doe", "90010112345")
        self.account1.incoming_transfer(100)
        
        self.account2 = PersonalAccount("Jane", "Smith", "85020223456")
        self.account2.incoming_transfer(200)
    
    @patch('src.mongo_repository.MongoClient')
    def test_save_all_clears_collection_before_saving(self, mock_mongo_client):
        """Test: save_all() czyści kolekcję przed zapisem"""
        # Mockujemy całą strukturę MongoDB
        mock_collection = Mock()
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Zapisujemy konta
        accounts = [self.account1, self.account2]
        repo.save_all(accounts)
        
        # Sprawdzamy czy delete_many zostało wywołane
        mock_collection.delete_many.assert_called_once_with({})
    
    @patch('src.mongo_repository.MongoClient')
    def test_save_all_saves_all_accounts(self, mock_mongo_client):
        """Test: save_all() zapisuje wszystkie konta"""
        # Mockujemy strukturę MongoDB
        mock_collection = Mock()
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Zapisujemy konta
        accounts = [self.account1, self.account2]
        repo.save_all(accounts)
        
        # Sprawdzamy czy update_one wywołano 2 razy (dla każdego konta)
        assert mock_collection.update_one.call_count == 2
        
        # Sprawdzamy argumenty pierwszego wywołania
        first_call = mock_collection.update_one.call_args_list[0]
        assert first_call[0][0] == {"pesel": "90010112345"}
        assert first_call[1]["upsert"] is True
    
    @patch('src.mongo_repository.MongoClient')
    def test_load_all_returns_personal_accounts(self, mock_mongo_client):
        """Test: load_all() zwraca PersonalAccount z bazy"""
        # Mockujemy kolekcję z danymi
        mock_collection = Mock()
        mock_collection.find.return_value = [
            self.account1.to_dict(),
            self.account2.to_dict()
        ]
        
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Ładujemy konta
        accounts = repo.load_all()
        
        # Sprawdzamy czy zwrócono 2 konta
        assert len(accounts) == 2
        
        # Sprawdzamy czy są to PersonalAccount
        assert isinstance(accounts[0], PersonalAccount)
        assert isinstance(accounts[1], PersonalAccount)
        
        # Sprawdzamy dane pierwszego konta
        assert accounts[0].pesel == "90010112345"
        assert accounts[0].first_name == "John"
        assert accounts[0].balance == 100
    
    @patch('src.mongo_repository.MongoClient')
    @patch('src.company_account.CompanyAccount._validate_nip_with_mf')
    def test_load_all_returns_company_accounts(self, mock_validate_nip, mock_mongo_client):
        """Test: load_all() zwraca CompanyAccount z bazy"""
        # Mockujemy walidację NIP
        mock_validate_nip.return_value = True
        
        # Tworzymy CompanyAccount
        company = CompanyAccount("Test Corp", "1234567890")
        company.incoming_transfer(500)
        
        # Mockujemy kolekcję z danymi
        mock_collection = Mock()
        mock_collection.find.return_value = [
            company.to_dict()
        ]
        
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Ładujemy konta
        accounts = repo.load_all()
        
        # Sprawdzamy czy zwrócono 1 konto
        assert len(accounts) == 1
        
        # Sprawdzamy czy jest to CompanyAccount
        assert isinstance(accounts[0], CompanyAccount)
        
        # Sprawdzamy dane
        assert accounts[0].nip == "1234567890"
        assert accounts[0].company_name == "Test Corp"
        assert accounts[0].balance == 500
    
    @patch('src.mongo_repository.MongoClient')
    def test_load_all_skips_unknown_account_types(self, mock_mongo_client):
        """Test: load_all() pomija nieznane typy kont"""
        # Mockujemy kolekcję z danymi (w tym nieznany typ)
        mock_collection = Mock()
        mock_collection.find.return_value = [
            self.account1.to_dict(),
            {"type": "unknown", "data": "test"},  # Nieznany typ
            self.account2.to_dict()
        ]
        
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Ładujemy konta
        accounts = repo.load_all()
        
        # Sprawdzamy czy zwrócono tylko 2 konta (pominięto unknown)
        assert len(accounts) == 2
        assert isinstance(accounts[0], PersonalAccount)
        assert isinstance(accounts[1], PersonalAccount)
    
    @patch('src.mongo_repository.MongoClient')
    def test_save_all_uses_upsert(self, mock_mongo_client):
        """Test: save_all() używa upsert=True"""
        # Mockujemy strukturę MongoDB
        mock_collection = Mock()
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Zapisujemy jedno konto
        repo.save_all([self.account1])
        
        # Sprawdzamy czy update_one zostało wywołane z upsert=True
        call_args = mock_collection.update_one.call_args
        assert call_args[1]["upsert"] is True
    
    @patch('src.mongo_repository.MongoClient')
    def test_load_all_removes_mongodb_id(self, mock_mongo_client):
        """Test: load_all() usuwa _id z dokumentów MongoDB"""
        # Mockujemy kolekcję z danymi zawierającymi _id
        account_dict = self.account1.to_dict()
        account_dict["_id"] = "mongodb_object_id_12345"
        
        mock_collection = Mock()
        mock_collection.find.return_value = [account_dict]
        
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Ładujemy konta (nie powinno być błędu)
        accounts = repo.load_all()
        
        # Sprawdzamy czy konto zostało załadowane poprawnie
        assert len(accounts) == 1
        assert accounts[0].pesel == "90010112345"
    
    @patch('src.mongo_repository.MongoClient')
    def test_close_connection(self, mock_mongo_client):
        """Test: close() zamyka połączenie z MongoDB"""
        # Mockujemy strukturę MongoDB
        mock_collection = Mock()
        mock_db = Mock()
        mock_client_instance = Mock()
        
        mock_client_instance.__getitem__ = lambda self, key: mock_db
        mock_db.__getitem__ = lambda self, key: mock_collection
        mock_mongo_client.return_value = mock_client_instance
        
        # Tworzymy repository
        repo = MongoAccountsRepository()
        
        # Zamykamy połączenie
        repo.close()
        
        # Sprawdzamy czy close zostało wywołane na kliencie
        mock_client_instance.close.assert_called_once()
