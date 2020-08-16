import json

from web3 import Web3, HTTPProvider
from web3.gas_strategies.rpc import rpc_gas_price_strategy


class ContractInterface(object):
    def __init__(self, config):
        """
        sets up w3 and the contract
        """
        self.config = config
        self.provider = HTTPProvider(self.config.PROVIDER_URI)
        self.w3 = Web3(self.provider)
        self.w3.eth.setGasPriceStrategy(rpc_gas_price_strategy)
        # TODO implement logging and detailed error handling
        try:
            self.senderAccount = self.w3.eth.account.privateKeyToAccount(self.config.SENDER_KEY)
            with open(config.CONTRACT_JSON) as json_file:
                contract_json = json.load(json_file)
            self.contract = self.w3.eth.contract(
                Web3.toChecksumAddress(config.CONTRACT_ADDRESS),
                abi=contract_json['abi'])
        except Exception as e:
            print(str(e))

    def isConnected(self):
        # TODO implement logging
        try:
            print(self.w3.eth.blockNumber)
            print(self.w3.eth.gasPrice)
            print(self.w3.isConnected())
        except Exception as e:
            print(str(e))
        return self.w3.isConnected()

    def transact_raw(self, contract_fname, *args):
        """
        handle a contract function that is a transaction
        """
        contract_f = getattr(self.contract.functions, contract_fname)
        estimatedGas = contract_f(*args).estimateGas({'from': self.senderAccount.address})
        transaction = contract_f(*args).buildTransaction({
            'chainId': 1,
            'gas': estimatedGas,
            # Get gas price from the node (rpc strategy)
            'gasPrice': self.w3.eth.generateGasPrice(),
            # Get correct transaction nonce for sender from the node
            'nonce': self.w3.eth.getTransactionCount(self.senderAccount.address)
        })
        signed = self.w3.eth.account.signTransaction(transaction, self.senderAccount.privateKey)
        txHash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        return self.w3.eth.waitForTransactionReceipt(txHash)

    def __getattr__(self, name, *args, **kwargs):
        """
        all the call()s we redirect them to the contract functions
        (if a function by that name exists)
        """

        # pick up the contract function
        try:
            contract_f = getattr(self.contract.functions, name)
        except AttributeError:
            return super(ContractInterface, self).__getattr__(name, *args, **kwargs)

        def wrapper(*args, **kwargs):
            try:
                f_encoder = getattr(self, f'encode_{name}')
                encoded_args = f_encoder(*args)
            except AttributeError:
                encoded_args = args

            ret = contract_f(*encoded_args).call()
            # TODO: verify if this is consistent
            if ret == True:
                ret = self.transact_raw(name, *encoded_args)

            try:
                f_decoder = getattr(self, f'decode_{name}')
                return f_decoder(ret)
            except AttributeError:
                pass
            return ret

        return wrapper

