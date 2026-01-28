Feature: Money transfers

  Scenario: User can make incoming transfer
    Given Account registry is empty
    And I create an account using name: "john", last name: "smith", pesel: "90092909123"
    When I make an incoming transfer of "500" to account with pesel "90092909123"
    Then Account with pesel "90092909123" has balance equal to "500"

  Scenario: User can make multiple incoming transfers
    Given Account registry is empty
    And I create an account using name: "alice", last name: "wonder", pesel: "85092909456"
    When I make an incoming transfer of "100" to account with pesel "85092909456"
    And I make an incoming transfer of "200" to account with pesel "85092909456"
    And I make an incoming transfer of "300" to account with pesel "85092909456"
    Then Account with pesel "85092909456" has balance equal to "600"

  Scenario: User can make outgoing transfer with sufficient balance
    Given Account registry is empty
    And I create an account using name: "bob", last name: "builder", pesel: "92092909789"
    And I make an incoming transfer of "1000" to account with pesel "92092909789"
    When I make an outgoing transfer of "400" from account with pesel "92092909789"
    Then Account with pesel "92092909789" has balance equal to "600"

  Scenario: User cannot make outgoing transfer with insufficient balance
    Given Account registry is empty
    And I create an account using name: "charlie", last name: "brown", pesel: "88092909321"
    And I make an incoming transfer of "100" to account with pesel "88092909321"
    When I try to make an outgoing transfer of "500" from account with pesel "88092909321"
    Then The transfer should fail
    And Account with pesel "88092909321" has balance equal to "100"

  Scenario: User can make express transfer with fee
    Given Account registry is empty
    And I create an account using name: "david", last name: "jones", pesel: "91092909654"
    And I make an incoming transfer of "1000" to account with pesel "91092909654"
    When I make an express transfer of "200" from account with pesel "91092909654"
    Then Account with pesel "91092909654" has balance equal to "799"

  Scenario: Complex transfer flow
    Given Account registry is empty
    And I create an account using name: "emma", last name: "watson", pesel: "93092909987"
    When I make an incoming transfer of "2000" to account with pesel "93092909987"
    And I make an outgoing transfer of "500" from account with pesel "93092909987"
    And I make an incoming transfer of "300" to account with pesel "93092909987"
    And I make an express transfer of "100" from account with pesel "93092909987"
    Then Account with pesel "93092909987" has balance equal to "1699"
