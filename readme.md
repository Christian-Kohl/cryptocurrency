This is a practice project, that should not be used as a working system! It is neither secure nor reliable.

# Blockchain Project

With blockchain technology becoming more relevant in the last years, and new uses being popularized recently, such as NFTs. With this in mind, the goal of this project was to implement a basic blockchain cryptocurrency. This is mainly to understand the behind the scenes interactions that cause so much hype in financial markets nowadays.

The basic elements of a blockchain that have been implemented:
* Transactions, in this case a simple token
* Mining, in this case finding a fitting hash to create a new block, with payment in return
* Checks for validity, and verify users and transactions

With this functionality we are able to emulate similar transactions, using the same technology as a large cryptocurrency as bitcoin. The peinciples, in regards to the proof mechanism is the same. There is more functionality that would have to be implemented, especially on the server/node side.

## Outline of API

### /transaction/new (POST)

```
{
  'sender': 'nameOfSender',
  'recipient': 'nameOfRecipient',
  'amount': amountToTransact,
  'transactor': 'nameofeithersenderorrecipient',
  'password': 'passwordOfTransactor'
}
  ```
  Create a new transaction between two users, the transactor and their passwords have to be given to verify the user. Once both users have sent the same request (barring the transactor and password), the transaction will be added to the next block.
  
  ### /mine (GET)
  
  This is a testing api call, which automatically solves the problem to create the next block, as this is for testing, the base user 'Christian' will be given the reward for mining the block.
  
  ### /mine (POST)
  
```
{
  'miner': 'miner',
  'proof': 'proof_no'
}
```
This API call allows for the user to mine a block themselves, the password does not have to be checked as there is no downside for the miner given.
  
  This method is for a user to mine a block themselves, allowing a user to be set.
  
### /chain (GET)

Returns the current chain up to the point of call.

### /user/new (POST)

```
{
  'user': 'username',
  'pass': 'password'
}
```

Creates a new user, with an amount of 0 currently in their wallet.
