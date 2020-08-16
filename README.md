# ethcc
Ethereum smart contracts interface on top of web3py

In `example.py` you can find a definition for a `flag map` smart contract where you have two methods, `updateFlagCoords` and `flagIdToCoords`. Those two methods are said to accept and return an array of two ints, and in the model you can see how that is handled, so by defining an `encode` method and a `decode` method: those two will be automatically picked up - if defined - by the contract interface (`ethcc/contract_interface.py`).

TODO:
* add contract creation
* add logging
* add tests
