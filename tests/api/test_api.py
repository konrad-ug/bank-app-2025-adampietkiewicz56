import requests
import pytest




class TestApi:

    url  = "http://127.0.0.1:5000/api/accounts"



    def set_up(self):
        self.pesel = "12345678901" 
        payload = {
            "name": "John",
            "surname": "Doe",
            "pesel": self.pesel
        }
        response = requests.post(url, json=payload)
        assert response.status_code == 201
        yield
        all_accounts = requests.get(f"{self.url}/accounts").json()
        for account in all_accounts:
            requests.delete(f"{self.url}/accounts/{account['pesel']}")




    def test_create_account(self):
        url = f"{self.url}/accounts"
        payload = {
            "name": "John",
            "surname": "Doe",
            "pesel": "12345678901"
        }


    def test_get_account_count(self):
        url = f"{self.url}/accounts/count"
        res = requests.get(url)
        assert res.status_code == 200
        assert res.json()['count'] == 1

    
    def test_get_account_by_pesel(self):
        pesel = "12345678901"  
        get_res = requests.get(f"{self.url}/{pesel}")
        assert get_res.status_code == 200

        account = get_res.json()
        assert account["name"] == "John"
        assert account["surname"] == "Doe"
        assert account["pesel"] == pesel
       
        

