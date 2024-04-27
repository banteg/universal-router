import pytest

from uniswap.universal_router import Commands, encode_command

weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
yfi = "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e"
fee = 10000
amount = 10**18
amount_min = 1234
payer_is_user = False
encoded = bytes.fromhex(
    "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000004d200000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002bc02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000000000000000000000"
)

swaps = [
    {"command": Commands.V3_SWAP_EXACT_IN, "path": [weth, fee, yfi], "encoded": encoded},
    {
        "command": Commands.V3_SWAP_EXACT_IN,
        "path": bytes.fromhex(
            "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e"
        ),
        "encoded": encoded,
    },
    {
        "command": Commands.V3_SWAP_EXACT_OUT,
        "path": [weth, fee, yfi],
        "encoded": encoded,
    },
    {
        "command": Commands.V3_SWAP_EXACT_OUT,
        "path": bytes.fromhex(
            "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e"
        ),
        "encoded": encoded,
    },
]


@pytest.mark.parametrize("payload", swaps)
def test_encode_swap(payload, accounts):
    command, data = encode_command(
        payload["command"], str(accounts[0]), amount, amount_min, payload["path"], payer_is_user
    )
    assert command == payload["command"]
    assert data == payload["encoded"]
