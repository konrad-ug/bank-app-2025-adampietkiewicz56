from pymongo import MongoClient


class MongoAccountsRepository:
    """Repository dla zarządzania kontami w MongoDB"""
    
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="bank_app"):
        """
        Inicjalizuje połączenie z MongoDB
        
        Args:
            connection_string: String połączenia do MongoDB
            database_name: Nazwa bazy danych
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self._collection = self.db["accounts"]
    
    def save_all(self, accounts):
        """
        Zapisuje wszystkie konta do bazy danych.
        Przed zapisem czyści kolekcję (tylko aktualne konta).
        
        Args:
            accounts: Lista obiektów Account do zapisania
        """
        # Czyścimy kolekcję przed zapisem
        self._collection.delete_many({})
        
        # Zapisujemy wszystkie konta
        for account in accounts:
            self._collection.update_one(
                {"pesel": account.pesel},
                {"$set": account.to_dict()},
                upsert=True,
            )
    
    def load_all(self):
        """
        Ładuje wszystkie konta z bazy danych.
        
        Returns:
            Lista obiektów Account załadowanych z bazy
        """
        from src.personal_account import PersonalAccount
        from src.company_account import CompanyAccount
        
        accounts = []
        for account_dict in self._collection.find():
            # Usuwamy _id MongoDB (nie potrzebne w obiekcie)
            account_dict.pop("_id", None)
            
            # Rekonstruujemy obiekt na podstawie typu
            if account_dict.get("type") == "personal":
                account = PersonalAccount.from_dict(account_dict)
            elif account_dict.get("type") == "company":
                account = CompanyAccount.from_dict(account_dict)
            else:
                continue  # Pomijamy nieznane typy
            
            accounts.append(account)
        
        return accounts
    
    def close(self):
        """Zamyka połączenie z MongoDB"""
        self.client.close()
