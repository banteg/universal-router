from enum import IntEnum
from itertools import cycle

from eth_abi import encode
from eth_abi.packed import encode_packed


class Commands(IntEnum):
    """
    @dev see https://github.com/Uniswap/universal-router/blob/main/contracts/libraries/Commands.sol
    """

    # Masks to extract certain bits of commands
    FLAG_ALLOW_REVERT = 0x80
    COMMAND_TYPE_MASK = 0x3F

    # Command Types. Maximum supported command at this moment is 0x3f.

    # Command Types where value<0x08, executed in the first nested-if block
    V3_SWAP_EXACT_IN = 0x00
    V3_SWAP_EXACT_OUT = 0x01
    PERMIT2_TRANSFER_FROM = 0x02
    PERMIT2_PERMIT_BATCH = 0x03
    SWEEP = 0x04
    TRANSFER = 0x05
    PAY_PORTION = 0x06
    # COMMAND_PLACEHOLDER = 0x07

    # The commands are executed in nested if blocks to minimise gas consumption
    # The following constant defines one of the boundaries where the if blocks split commands
    FIRST_IF_BOUNDARY = 0x08

    # Command Types where 0x08<=value<=0x0f, executed in the second nested-if block
    V2_SWAP_EXACT_IN = 0x08
    V2_SWAP_EXACT_OUT = 0x09
    PERMIT2_PERMIT = 0x0A
    WRAP_ETH = 0x0B
    UNWRAP_WETH = 0x0C
    PERMIT2_TRANSFER_FROM_BATCH = 0x0D
    BALANCE_CHECK_ERC20 = 0x0E
    # COMMAND_PLACEHOLDER = 0x0f

    # The commands are executed in nested if blocks to minimise gas consumption
    # The following constant defines one of the boundaries where the if blocks split commands
    SECOND_IF_BOUNDARY = 0x10

    # Command Types where 0x10<=value<0x18, executed in the third nested-if block
    SEAPORT_V1_5 = 0x10
    LOOKS_RARE_V2 = 0x11
    NFTX = 0x12
    CRYPTOPUNKS = 0x13
    # 0x14
    OWNER_CHECK_721 = 0x15
    OWNER_CHECK_1155 = 0x16
    SWEEP_ERC721 = 0x17

    # The commands are executed in nested if blocks to minimise gas consumption
    # The following constant defines one of the boundaries where the if blocks split commands
    THIRD_IF_BOUNDARY = 0x18

    # Command Types where 0x18<=value<=0x1f, executed in the final nested-if block
    X2Y2_721 = 0x18
    SUDOSWAP = 0x19
    NFT20 = 0x1A
    X2Y2_1155 = 0x1B
    FOUNDATION = 0x1C
    SWEEP_ERC1155 = 0x1D
    ELEMENT_MARKET = 0x1E
    # COMMAND_PLACEHOLDER = 0x1f

    # The commands are executed in nested if blocks to minimise gas consumption
    # The following constant defines one of the boundaries where the if blocks split commands
    FOURTH_IF_BOUNDARY = 0x20

    # Command Types where 0x20<=value
    SEAPORT_V1_4 = 0x20
    EXECUTE_SUB_PLAN = 0x21
    APPROVE_ERC20 = 0x22
    # COMMAND_PLACEHOLDER for 0x23 to 0x3f (all unused)


def encode_path(path: list) -> bytes:
    types = [type for _, type in zip(path, cycle(["address", "uint24"]))]
    return encode_packed(types, path)


def encode_command(command: Commands, *args):
    match command, args:
        case Commands.V3_SWAP_EXACT_IN, (
            str(recipient),
            int(amount_in),
            int(amount_out_min),
            bytes(path),
            bool(payer_is_user),
        ):
            return (
                Commands.V3_SWAP_EXACT_IN,
                encode(
                    ["address", "uint256", "uint256", "bytes", "bool"],
                    [recipient, amount_in, amount_out_min, path, payer_is_user],
                ),
            )
        case Commands.V3_SWAP_EXACT_IN, (
            str(recipient),
            int(amount_in),
            int(amount_out_min),
            list(path),
            bool(payer_is_user),
        ):
            path = encode_path(path)
            return (
                Commands.V3_SWAP_EXACT_IN,
                encode(
                    ["address", "uint256", "uint256", "bytes", "bool"],
                    [recipient, amount_in, amount_out_min, path, payer_is_user],
                ),
            )
        case _:
            raise NotImplementedError("unknown command or param types")
