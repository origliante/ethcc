from web3.auto.gethdev import w3
from eth_abi import encode_abi, decode_abi, is_encodable
from eth_abi.packed import encode_abi_packed

from ethcc import ContractInterface


class FlagMap(ContractInterface):
    def validate_coords(self, lat, lon):
        if lat < -600000000 or lat > 600000000 or \
            lon < -1200000000 or lon > 1200000000:
            raise ValueError("lat and/or lon outside boundaries.")
        return True

    def encode_updateFlagCoords(self, flagId, args):
        lat, lon = args
        self.validate_coords(lat, lon)
        if not w3.is_encodable('int[2]', [lat, lon]):
            raise ValueError("lat and lon must be ints.")
        return flagId, encode_abi_packed(['int[]', ], ([lat, lon], ))

    def decode_flagIdToCoords(self, encoded):
        lat, lon = decode_abi(['int', 'int'], encoded)
        return lat, lon


if __name__ == '__main__':
    import sys
    import example_config as config

    contract = FlagMap(config)
    if not contract.isConnected():
        print('contract not connected, exiting.')
        sys.exit(-1)

    r = contract.updateFlagCoords(1234, (10, 10))
    print(r)

    r = contract.flagIdToCoords(1234)
    print(r)

