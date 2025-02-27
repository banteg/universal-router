"""
Universal Router Python interface.

This module provides Python bindings for Uniswap's Universal Router, allowing the construction
and encoding of complex multi-step transactions into a single atomic execution.
"""

from enum import IntEnum
from itertools import cycle
from typing import NamedTuple, Any

from eth_abi import encode
from eth_abi.packed import encode_packed
from pydantic import BaseModel, TypeAdapter


class Command(IntEnum):
    """
    Enumeration of all supported Universal Router commands.
    
    These values correspond to the command identifiers in the Universal Router contract.
    See: https://github.com/Uniswap/universal-router/blob/v1.6.0/contracts/libraries/Commands.sol
    """

    # Masks to extract certain bits of commands
    FLAG_ALLOW_REVERT = 0x80  # Flag to mark a command as allowed to revert
    COMMAND_TYPE_MASK = 0x3F  # Mask to extract the command type

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


REVERTIBLE_COMMANDS = {
    Command.SEAPORT_V1_5,
    Command.SEAPORT_V1_4,
    Command.NFTX,
    Command.LOOKS_RARE_V2,
    Command.X2Y2_721,
    Command.X2Y2_1155,
    Command.FOUNDATION,
    Command.SUDOSWAP,
    Command.NFT20,
    Command.EXECUTE_SUB_PLAN,
    Command.CRYPTOPUNKS,
    Command.ELEMENT_MARKET,
}


class PermitDetails(NamedTuple):
    """
    Details for a token permit.
    
    Corresponds to the PermitDetails struct in Permit2 contract.
    https://github.com/Uniswap/permit2/blob/main/src/interfaces/IAllowanceTransfer.sol
    """
    token: str  # Token address
    amount: int  # Token amount
    expiration: int  # Timestamp when the permit expires
    nonce: int  # Nonce for the permit


class PermitSingle(NamedTuple):
    """
    Single permit data structure.
    
    Corresponds to the PermitSingle struct in Permit2 contract.
    """
    details: PermitDetails  # Permit details
    spender: str  # Address allowed to spend the tokens
    sigDeadline: int  # Timestamp until which the signature is valid


class PermitBatch(NamedTuple):
    """
    Batch of permits data structure.
    
    Corresponds to the PermitBatch struct in Permit2 contract.
    """
    details: list[PermitDetails]  # List of permit details
    spender: str  # Address allowed to spend the tokens
    sigDeadline: int  # Timestamp until which the signature is valid


class AllowanceTransferDetails(NamedTuple):
    """
    Details for token transfer from an allowance.
    
    Corresponds to the AllowanceTransferDetails struct in Permit2 contract.
    """
    owner: str  # Token owner
    to: str  # Recipient of the transfer
    amount: int  # Token amount
    token: str  # Token address


# use pydantic type adapter to do nested casting so you can pass as dict
permit_batch_adapter = TypeAdapter(PermitBatch)
permit_single_adapter = TypeAdapter(PermitSingle)
transfer_from_batch_adapter = TypeAdapter(list[AllowanceTransferDetails])


def encode_path(path: list[str | int]) -> bytes:
    """
    Encode a Uniswap V3 path for swap.
    
    A path consists of alternating token addresses and fee tiers.
    E.g. [token_in, fee, token_out] or [token_in, fee1, token_mid, fee2, token_out]
    
    Args:
        path: List of token addresses and fee tiers
        
    Returns:
        Packed binary encoding of the path
    """
    types = [type for _, type in zip(path, cycle(["address", "uint24"]))]
    return encode_packed(types, path)


def encode_command(command: Command, *args) -> bytes:
    """
    Encode a Universal Router command with its parameters.
    
    Each command has specific parameter requirements, handled by pattern matching the command type.
    
    Args:
        command: The command type from the Command enum
        *args: Command-specific parameters
        
    Returns:
        ABI-encoded parameters for the command
        
    Raises:
        NotImplementedError: If the command or parameter types are unknown
    
    See: https://github.com/Uniswap/universal-router/blob/main/contracts/base/Dispatcher.sol
    """
    match command, args:
        case Command.V3_SWAP_EXACT_IN | Command.V3_SWAP_EXACT_OUT, [
            str(recipient),
            int(amount),
            int(amount_min),
            list(path)
            | bytes(path),
            bool(payer_is_user),
        ]:
            if isinstance(path, list):
                path = encode_path(path)
            return encode(
                ["address", "uint256", "uint256", "bytes", "bool"],
                [recipient, amount, amount_min, path, payer_is_user],
            )
        case Command.PERMIT2_TRANSFER_FROM, [str(token), str(recipient), int(amount)]:
            return encode(
                ["address", "address", "uint160"],
                [token, recipient, amount],
            )
        case Command.PERMIT2_TRANSFER_FROM_BATCH, [list(batch_details)]:
            batch_details = transfer_from_batch_adapter.validate_python(batch_details)
            return encode(
                ["(address,address,uint160,address)[]"],
                [batch_details],
            )
        case Command.PERMIT2_PERMIT, [
            dict(permit_single)
            | list(permit_single)
            | tuple(permit_single),
            bytes(data),
        ]:
            permit_single = permit_single_adapter.validate_python(permit_single)
            return encode(
                ["((address,uint160,uint48,uint48),address,uint256)", "bytes"],  # noqa: E501
                [permit_single, data],
            )
        case Command.PERMIT2_PERMIT_BATCH, [
            dict(permit_batch)
            | list(permit_batch)
            | tuple(permit_batch),
            bytes(data),
        ]:
            permit_batch = permit_batch_adapter.validate_python(permit_batch)
            return encode(
                ["((address,uint160,uint48,uint48)[],address,uint256)", "bytes"],  # noqa: E501
                [permit_batch, data],
            )
        case Command.SWEEP, [str(token), str(recipient), int(amount_min)]:
            return encode(
                ["address", "address", "uint256"],
                [token, recipient, amount_min],
            )
        case Command.TRANSFER, [str(token), str(recipient), int(amount)]:
            return encode(
                ["address", "address", "uint256"],
                [token, recipient, amount],
            )
        case Command.PAY_PORTION, [str(token), str(recipient), int(bips)]:
            return encode(
                ["address", "address", "uint256"],
                [token, recipient, bips],
            )
        case Command.V2_SWAP_EXACT_IN | Command.V2_SWAP_EXACT_OUT, [
            str(recipient),
            int(amount),
            int(amount_min),
            list(path),
            bool(payer_is_user),
        ]:
            return encode(
                ["address", "uint256", "uint256", "address[]", "bool"],
                [recipient, amount, amount_min, path, payer_is_user],
            )
        case Command.WRAP_ETH, [str(recipient), int(amount_min)]:
            return encode(
                ["address", "uint256"],
                [recipient, amount_min],
            )
        case Command.UNWRAP_WETH, [str(recipient), int(amount_min)]:
            return encode(
                ["address", "uint256"],
                [recipient, amount_min],
            )
        case Command.BALANCE_CHECK_ERC20, [str(owner), str(token), int(min_balance)]:
            return encode(
                ["address", "address", "uint256"],
                [owner, token, min_balance],
            )
        case (
            Command.SEAPORT_V1_5
            | Command.SEAPORT_V1_4
            | Command.LOOKS_RARE_V2
            | Command.NFTX
            | Command.ELEMENT_MARKET
            | Command.SUDOSWAP
            | Command.NFT20,
            [int(value), bytes(data)],
        ):
            # TODO nft order encoding
            return encode(
                ["uint256", "bytes"],
                [value, data],
            )
        case Command.CRYPTOPUNKS, [int(punk_id), str(recipient), int(value)]:
            return encode(
                ["uint256", "address", "uint256"],
                [punk_id, recipient, value],
            )
        case Command.OWNER_CHECK_721, [str(owner), str(token), int(id)]:
            return encode(
                ["address", "address", "uint256"],
                [owner, token, id],
            )
        case Command.OWNER_CHECK_1155, [str(owner), str(token), int(id), int(min_balance)]:
            return encode(
                ["address", "address", "uint256", "uint256"],
                [owner, token, id, min_balance],
            )
        case Command.SWEEP_ERC721, [str(token), str(recipient), int(id)]:
            return encode(
                ["address", "address", "uint256"],
                [token, recipient, id],
            )
        case Command.X2Y2_721, [int(value), bytes(data), str(recipient), str(token), int(id)]:
            return encode(
                ["uint256", "bytes", "address", "address", "uint256"],
                [value, data, recipient, token, id],
            )
        case Command.X2Y2_1155, [
            int(value),
            bytes(data),
            str(recipient),
            str(token),
            int(id),
            int(amount),
        ]:
            return encode(
                ["uint256", "bytes", "address", "address", "uint256", "uint256"],
                [value, data, recipient, token, id, amount],
            )
        case Command.FOUNDATION, [int(value), bytes(data), str(recipient), str(token), int(id)]:
            return encode(
                ["uint256", "bytes", "address", "address", "uint256"],
                [value, data, recipient, token, id],
            )
        case Command.SWEEP_ERC1155, [str(token), str(recipient), int(id), int(amount)]:
            return encode(
                ["address", "address", "uint256", "uint256"],
                [token, recipient, id, amount],
            )
        case Command.EXECUTE_SUB_PLAN, [bytes(commands), list(inputs)]:
            return encode(
                ["bytes", "bytes[]"],
                [commands, inputs],
            )
        case Command.APPROVE_ERC20, [str(token), int(spender)]:
            return encode(
                ["address", "uint8"],
                [token, spender],
            )
        case _:
            raise NotImplementedError("unknown command or param types")


class Planner(BaseModel):
    """
    Builder for Universal Router command sequences.
    
    The Planner helps construct a series of commands to be executed atomically by the
    Universal Router contract. It manages command collection and encoding.
    """
    commands: list[Command] = []
    inputs: list[list[Any]] = []

    def add(self, command: Command, *args, allow_revert: bool = False):
        """
        Add a command to the execution plan.
        
        Args:
            command: The command type from the Command enum
            *args: Command-specific parameters
            allow_revert: Whether this command is allowed to revert
                          (only applicable for specific commands)
                          
        Returns:
            self: For method chaining
            
        Raises:
            ValueError: If the command cannot be allowed to revert but allow_revert is True
        """
        if allow_revert:
            if command not in REVERTIBLE_COMMANDS:
                raise ValueError(f"{command.name} cannot be allowed to revert")
            command |= Command.FLAG_ALLOW_REVERT

        # Validate the command and args are encodeable
        encode_command(command, *args)
        self.commands.append(command)
        self.inputs.append(args)
        return self

    def build(self) -> tuple[bytes, list[bytes]]:
        """
        Build the final command and input arrays for the Universal Router.
        
        Returns:
            A tuple of (commands, inputs) where:
            - commands: Bytes containing the command identifiers
            - inputs: List of encoded command parameters
        """
        commands = bytes(self.commands)
        inputs = [
            encode_command(command, *args) for command, args in zip(self.commands, self.inputs)
        ]
        return commands, inputs

    def v3_swap_exact_in(
        self,
        recipient: str,
        amount: int,
        amount_min: int,
        path: list | bytes,
        payer_is_user: bool,
        allow_revert: bool = False,
    ):
        """
        Add a Uniswap V3 exactInput swap command.
        
        Args:
            recipient: Address that will receive the output tokens
            amount: Exact amount of input tokens to swap
            amount_min: Minimum amount of output tokens to receive
            path: Token path as either a list [tokenIn, fee, tokenOut] or pre-encoded bytes
            payer_is_user: Whether the input tokens come from the transaction sender
            allow_revert: Whether this command is allowed to revert
            
        Returns:
            self: For method chaining
        """
        self.add(
            Command.V3_SWAP_EXACT_IN,
            recipient,
            amount,
            amount_min,
            path,
            payer_is_user,
            allow_revert=allow_revert,
        )

    def v3_swap_exact_out(
        self,
        recipient: str,
        amount: int,
        amount_min: int,
        path: list | bytes,
        payer_is_user: bool,
        allow_revert=False,
    ):
        self.add(
            Command.V3_SWAP_EXACT_OUT,
            recipient,
            amount,
            amount_min,
            path,
            payer_is_user,
            allow_revert=allow_revert,
        )

    def permit2_transfer_from(self, token: str, recipient: str, amount: int, allow_revert=False):
        self.add(Command.PERMIT2_TRANSFER_FROM, token, recipient, amount, allow_revert=allow_revert)

    def permit2_transfer_from_batch(
        self, batch_details: list[AllowanceTransferDetails], allow_revert=False
    ):
        self.add(Command.PERMIT2_TRANSFER_FROM_BATCH, batch_details, allow_revert=allow_revert)

    def permit2_permit(self, permit_single: PermitSingle, data: bytes, allow_revert=False):
        self.add(Command.PERMIT2_PERMIT, permit_single, data, allow_revert=allow_revert)

    def permit2_permit_batch(self, permit_batch: PermitBatch, data: bytes, allow_revert=False):
        self.add(Command.PERMIT2_PERMIT_BATCH, permit_batch, data, allow_revert=allow_revert)

    def sweep(self, token: str, recipient: str, amount_min: int, allow_revert=False):
        self.add(Command.SWEEP, token, recipient, amount_min, allow_revert=allow_revert)

    def transfer(self, token: str, recipient: str, amount: int, allow_revert=False):
        self.add(Command.TRANSFER, token, recipient, amount, allow_revert=allow_revert)

    def pay_portion(self, token: str, recipient: str, bips: int, allow_revert=False):
        self.add(Command.PAY_PORTION, token, recipient, bips, allow_revert=allow_revert)

    def v2_swap_exact_in(
        self,
        recipient: str,
        amount: int,
        amount_min: int,
        path: list,
        payer_is_user: bool,
        allow_revert=False,
    ):
        self.add(
            Command.V2_SWAP_EXACT_IN,
            recipient,
            amount,
            amount_min,
            path,
            payer_is_user,
            allow_revert=allow_revert,
        )

    def v2_swap_exact_out(
        self,
        recipient: str,
        amount: int,
        amount_min: int,
        path: list,
        payer_is_user: bool,
        allow_revert=False,
    ):
        self.add(
            Command.V2_SWAP_EXACT_OUT,
            recipient,
            amount,
            amount_min,
            path,
            payer_is_user,
            allow_revert=allow_revert,
        )

    def wrap_eth(self, recipient: str, amount_min: int):
        """
        Add a command to wrap ETH into WETH.
        
        Args:
            recipient: Address that will receive the WETH
            amount_min: Amount of ETH to wrap
            
        Returns:
            self: For method chaining
        """
        self.add(Command.WRAP_ETH, recipient, amount_min)

    def unwrap_weth(self, recipient: str, amount_min: int):
        """
        Add a command to unwrap WETH back into ETH.
        
        Args:
            recipient: Address that will receive the ETH
            amount_min: Amount of WETH to unwrap
            
        Returns:
            self: For method chaining
        """
        self.add(Command.UNWRAP_WETH, recipient, amount_min)

    def balance_check_erc20(self, owner: str, token: str, min_balance: int):
        self.add(Command.BALANCE_CHECK_ERC20, owner, token, min_balance)

    def seaport_v1_5(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.SEAPORT_V1_5, value, data, allow_revert=allow_revert)

    def seaport_v1_4(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.SEAPORT_V1_4, value, data, allow_revert=allow_revert)

    def looks_rare_v2(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.LOOKS_RARE_V2, value, data, allow_revert=allow_revert)

    def nftx(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.NFTX, value, data, allow_revert=allow_revert)

    def element_market(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.ELEMENT_MARKET, value, data, allow_revert=allow_revert)

    def sudoswap(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.SUDOSWAP, value, data, allow_revert=allow_revert)

    def nft20(self, value: int, data: bytes, allow_revert=False):
        self.add(Command.NFT20, value, data, allow_revert=allow_revert)

    def cryptopunks(self, punk_id: int, recipient: str, value: int, allow_revert=False):
        self.add(Command.CRYPTOPUNKS, punk_id, recipient, value, allow_revert=allow_revert)

    def owner_check_721(self, owner: str, token: str, id: int):
        self.add(Command.OWNER_CHECK_721, owner, token, id)

    def owner_check_1155(self, owner: str, token: str, id: int, min_balance: int):
        self.add(Command.OWNER_CHECK_1155, owner, token, id, min_balance)

    def sweep_erc721(self, token: str, recipient: str, id: int):
        self.add(Command.SWEEP_ERC721, token, recipient, id)

    def x2y2_721(
        self, value: int, data: bytes, recipient: str, token: str, id: int, allow_revert=False
    ):
        self.add(Command.X2Y2_721, value, data, recipient, token, id, allow_revert=allow_revert)

    def x2y2_1155(
        self,
        value: int,
        data: bytes,
        recipient: str,
        token: str,
        id: int,
        amount: int,
        allow_revert=False,
    ):
        self.add(
            Command.X2Y2_1155, value, data, recipient, token, id, amount, allow_revert=allow_revert
        )

    def foundation(
        self, value: int, data: bytes, recipient: str, token: str, id: int, allow_revert=False
    ):
        self.add(Command.FOUNDATION, value, data, recipient, token, id, allow_revert=allow_revert)

    def sweep_erc1155(self, token: str, recipient: str, id: int, amount: int):
        self.add(Command.SWEEP_ERC1155, token, recipient, id, amount)

    def execute_sub_plan(self, commands: bytes, inputs: list[bytes], allow_revert=False):
        self.add(Command.EXECUTE_SUB_PLAN, commands, inputs, allow_revert=allow_revert)

    def approve_erc20(self, token: str, spender: int):
        """
        Add a command to approve an ERC20 token for spending.
        
        Args:
            token: The ERC20 token address
            spender: 1 to enable approval, 0 to disable
            
        Returns:
            self: For method chaining
        """
        self.add(Command.APPROVE_ERC20, token, spender)
