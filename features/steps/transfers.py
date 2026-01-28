from behave import *
import requests

URL = "http://localhost:5000"


@when('I make an incoming transfer of "{amount}" to account with pesel "{pesel}"')
@given('I make an incoming transfer of "{amount}" to account with pesel "{pesel}"')
def make_incoming_transfer(context, amount, pesel):
    json_body = {
        "type": "incoming",
        "amount": int(amount)
    }
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, f"Incoming transfer failed with status {response.status_code}"


@when('I make an outgoing transfer of "{amount}" from account with pesel "{pesel}"')
@given('I make an outgoing transfer of "{amount}" from account with pesel "{pesel}"')
def make_outgoing_transfer(context, amount, pesel):
    json_body = {
        "type": "outgoing",
        "amount": int(amount)
    }
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, f"Outgoing transfer failed with status {response.status_code}"


@when('I try to make an outgoing transfer of "{amount}" from account with pesel "{pesel}"')
def try_make_outgoing_transfer(context, amount, pesel):
    json_body = {
        "type": "outgoing",
        "amount": int(amount)
    }
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    # Zapisz status odpowiedzi w kontekście dla późniejszej weryfikacji
    context.last_response_status = response.status_code


@when('I make an express transfer of "{amount}" from account with pesel "{pesel}"')
def make_express_transfer(context, amount, pesel):
    json_body = {
        "type": "express",
        "amount": int(amount)
    }
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, f"Express transfer failed with status {response.status_code}"


@then('Account with pesel "{pesel}" has balance equal to "{balance}"')
def check_balance(context, pesel, balance):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200, f"Account with pesel {pesel} not found"
    
    account = response.json()
    actual_balance = account.get("balance", 0)
    expected_balance = int(balance)
    
    assert actual_balance == expected_balance, f"Expected balance {expected_balance}, but got {actual_balance}"


@then('The transfer should fail')
def check_transfer_failed(context):
    # Sprawdź czy ostatnia operacja zwróciła błąd
    assert hasattr(context, 'last_response_status'), "No transfer attempt was made"
    assert context.last_response_status == 400, f"Expected status 400, but got {context.last_response_status}"
