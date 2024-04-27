import pytest

from uniswap.universal_router import Commands, encode_command

dev = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
yfi = "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e"
fee = 10000
amount = 10**18
value = amount
amount_min = 1234
bips = 100
token_id = 1234
payer_is_user = False
data = b"hentai is art"
reference = {
    "v3_swap": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000004d200000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002bc02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000000000000000000000",
    "sweep": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb9226600000000000000000000000000000000000000000000000000000000000004d2",
    "transfer": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a7640000",
    "pay_portion": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000000000000000064",
    "v2_swap": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000004d200000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e",
    "wrap_eth": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a7640000",
    "balance_check": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e0000000000000000000000000000000000000000000000000de0b6b3a7640000",
    "nft_swap_mock": "0000000000000000000000000000000000000000000000000de0b6b3a76400000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000d68656e7461692069732061727400000000000000000000000000000000000000",
    "buy_punk": "00000000000000000000000000000000000000000000000000000000000004d2000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a7640000",
    "owner_721": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e00000000000000000000000000000000000000000000000000000000000004d2",
    "owner_1155": "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e00000000000000000000000000000000000000000000000000000000000004d20000000000000000000000000000000000000000000000000000000000000001",
    "sweep_721": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb9226600000000000000000000000000000000000000000000000000000000000004d2",
    "sweep_1155": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb9226600000000000000000000000000000000000000000000000000000000000004d20000000000000000000000000000000000000000000000000de0b6b3a7640000",
    "approve_erc20": "0000000000000000000000000bc529c00c6401aef6d220be8c6ea1667f6ad93e0000000000000000000000000000000000000000000000000000000000000001",
}
reference = {key: bytes.fromhex(value) for key, value in reference.items()}


@pytest.mark.parametrize(
    "payload",
    [
        {
            "command": Commands.V3_SWAP_EXACT_IN,
            "path": [weth, fee, yfi],
            "encoded": reference["v3_swap"],
        },
        {
            "command": Commands.V3_SWAP_EXACT_IN,
            "path": bytes.fromhex(
                "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e"
            ),
            "encoded": reference["v3_swap"],
        },
        {
            "command": Commands.V3_SWAP_EXACT_OUT,
            "path": [weth, fee, yfi],
            "encoded": reference["v3_swap"],
        },
        {
            "command": Commands.V3_SWAP_EXACT_OUT,
            "path": bytes.fromhex(
                "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20027100bc529c00c6401aef6d220be8c6ea1667f6ad93e"
            ),
            "encoded": reference["v3_swap"],
        },
    ],
)
def test_encode_swap(payload):
    assert (
        encode_command(payload["command"], dev, amount, amount_min, payload["path"], payer_is_user)
        == payload["encoded"]
    )


def test_encode_permit_transfer_from():
    assert encode_command(Commands.PERMIT2_TRANSFER_FROM, yfi, dev, amount) == reference["transfer"]


def test_encode_permit2_permit_batch():
    permit_batch = {...}  # Placeholder for the permit_batch dictionary
    data = b"..."  # Placeholder for the data bytes
    encoded_data = encode_command(Commands.PERMIT2_PERMIT_BATCH, permit_batch, data)
    assert encoded_data == b"..."  # Placeholder for the expected encoded data


def test_encode_sweep():
    assert encode_command(Commands.SWEEP, yfi, dev, amount_min) == reference["sweep"]


def test_encode_transfer():
    assert encode_command(Commands.TRANSFER, yfi, dev, amount) == reference["transfer"]


def test_encode_pay_portion():
    assert encode_command(Commands.PAY_PORTION, yfi, dev, bips) == reference["pay_portion"]


def test_encode_v2_swap_exact_in():
    assert (
        encode_command(
            Commands.V2_SWAP_EXACT_IN, dev, amount, amount_min, [weth, yfi], payer_is_user
        )
        == reference["v2_swap"]
    )


def test_encode_v2_swap_exact_out():
    assert (
        encode_command(
            Commands.V2_SWAP_EXACT_OUT, dev, amount, amount_min, [weth, yfi], payer_is_user
        )
        == reference["v2_swap"]
    )


def test_encode_permit2_permit():
    permit_single = {...}  # Placeholder for the permit_single dictionary
    data = b"..."  # Placeholder for the data bytes
    encoded_data = encode_command(Commands.PERMIT2_PERMIT, permit_single, data)
    assert encoded_data == b"..."  # Placeholder for the expected encoded data


def test_encode_wrap_eth():
    assert encode_command(Commands.WRAP_ETH, dev, amount) == reference["wrap_eth"]


def test_encode_unwrap_weth():
    assert encode_command(Commands.UNWRAP_WETH, dev, amount) == reference["wrap_eth"]


def test_encode_permit2_transfer_from_batch():
    batch_details = [...]  # Placeholder for the batch_details list
    data = encode_command(Commands.PERMIT2_TRANSFER_FROM_BATCH, batch_details)
    assert data == b"..."  # Placeholder for the expected encoded data


def test_encode_balance_check_erc20():
    assert (
        encode_command(Commands.BALANCE_CHECK_ERC20, dev, yfi, amount) == reference["balance_check"]
    )


def test_encode_seaport_v1_5():
    assert encode_command(Commands.SEAPORT_V1_5, amount, data) == reference["nft_swap_mock"]


def test_encode_looks_rare_v2():
    assert encode_command(Commands.LOOKS_RARE_V2, amount, data) == reference["nft_swap_mock"]


def test_encode_nftx():
    assert encode_command(Commands.NFTX, amount, data) == reference["nft_swap_mock"]


def test_encode_cryptopunks():
    assert encode_command(Commands.CRYPTOPUNKS, token_id, dev, amount) == reference["buy_punk"]


def test_encode_owner_check_721():
    assert encode_command(Commands.OWNER_CHECK_721, dev, yfi, token_id) == reference["owner_721"]


def test_encode_owner_check_1155():
    assert (
        encode_command(Commands.OWNER_CHECK_1155, dev, yfi, token_id, 1) == reference["owner_1155"]
    )


def test_encode_sweep_erc721():
    assert encode_command(Commands.SWEEP_ERC721, yfi, dev, token_id) == reference["sweep_721"]


def test_encode_x2y2_721():
    value = 10**18
    data = b"..."  # Placeholder for the data bytes
    token_id = 1234
    encoded_data = encode_command(Commands.X2Y2_721, value, data, dev, yfi, token_id)
    assert encoded_data == b"..."  # Placeholder for the expected encoded data


def test_encode_sudoswap():
    assert encode_command(Commands.SUDOSWAP, value, data) == reference["nft_swap_mock"]


def test_encode_nft20():
    assert encode_command(Commands.NFT20, value, data) == reference["nft_swap_mock"]


def test_encode_x2y2_1155():
    value = 10**18
    data = b"..."  # Placeholder for the data bytes
    token_id = 1234
    amount = 10
    encoded_data = encode_command(Commands.X2Y2_1155, value, data, dev, yfi, token_id, amount)
    assert encoded_data == b"..."  # Placeholder for the expected encoded data


def test_encode_foundation():
    value = 10**18
    data = b"..."  # Placeholder for the data bytes
    token_id = 1234
    encoded_data = encode_command(Commands.FOUNDATION, value, data, dev, yfi, token_id)
    assert encoded_data == b"..."  # Placeholder for the expected encoded data


def test_encode_sweep_erc1155():
    assert (
        encode_command(Commands.SWEEP_ERC1155, yfi, dev, token_id, amount)
        == reference["sweep_1155"]
    )


def test_encode_element_market():
    assert encode_command(Commands.ELEMENT_MARKET, value, data) == reference["nft_swap_mock"]


def test_encode_seaport_v1_4():
    assert encode_command(Commands.SEAPORT_V1_4, value, data) == reference["nft_swap_mock"]


def test_encode_execute_sub_plan():
    commands = b"..."  # Placeholder for the commands bytes
    inputs = [...]  # Placeholder for the inputs list
    data = encode_command(Commands.EXECUTE_SUB_PLAN, commands, inputs)
    assert data == b"..."  # Placeholder for the expected encoded data


def test_encode_approve_erc20():
    assert encode_command(Commands.APPROVE_ERC20, yfi, 1) == reference["approve_erc20"]
