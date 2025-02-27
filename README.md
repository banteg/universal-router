# Uniswap Universal Router Python Bindings

Python bindings for Uniswap's [Universal Router](https://github.com/Uniswap/universal-router) - an advanced trade router that allows batching complex multi-step trades atomically.

This library provides encoding functionality for Uniswap's Universal Router contract. It helps you build and encode transaction data but **does not send transactions**. You'll need to use a web3 library like [ape](https://github.com/ApeWorX/ape) or [web3.py](https://github.com/ethereum/web3.py) to actually submit the transactions to the Ethereum network.

## Installation

```bash
pip install git+https://github.com/banteg/universal-router.git
```

## Usage

### Basic Usage

```python
from uniswap.universal_router import Command, Planner

# Constants
recipient = "0x..."
weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
token = "0x..."
amount = 10**18
amount_min = 0
fee = 3000

# Create a plan
planner = Planner()

# Wrap ETH
planner.wrap_eth(recipient, amount)

# Swap WETH for token via Uniswap V3
planner.v3_swap_exact_in(
    recipient=recipient,
    amount=amount,
    amount_min=amount_min,
    path=[weth, fee, token],
    payer_is_user=False
)

# Get commands and inputs for the universal router contract
# - commands: encoded command identifiers to execute
# - inputs: encoded command parameters in the exact order they should be processed
commands, inputs = planner.build()
```

### Advanced Usage

This example shows how to use the library to execute a transaction with [ape](https://github.com/ApeWorX/ape) and
[dpack](https://github.com/banteg/dpack) for loading contracts.

```python
from dpack.ape import load
from ape import accounts, Contract, convert
from apt_tokens import tokens
from uniswap.universal_router import Planner

# Load your account
dev = accounts.load("dev")

# Load the Universal Router contract using dpack
uniswap = load("uniswap-v3.dpack.json")
universal_router = uniswap.universal_router

# Token addresses
weth = tokens['WETH']
usdc = tokens['USDC']

# Set up transaction parameters
amount = convert("1 ether", int)  # 1 ETH
amount_min = 0  # No minimum (in real usage, you should set a minimum)
fee = 500  # 0.05% fee tier

# Create the execution plan
planner = Planner()

# Wrap ETH - note the router itself is the recipient, we'll be able to use this amount in the next steps
planner.wrap_eth(str(universal_router), amount)

# Swap WETH for USDC via Uniswap V3
planner.v3_swap_exact_in(
    recipient=str(dev),
    amount=amount,
    amount_min=amount_min,
    path=[str(weth), fee, str(usdc)],
    payer_is_user=False
)

# Build the commands and inputs
commands, inputs = planner.build()

# Execute the transaction
tx = universal_router.execute(
    commands, 
    inputs,
    value=amount,
    sender=dev
)

# Check the result
usdc_balance = usdc.balanceOf(dev)
print("USDC balance:", convert(usdc_balance, 'USDC'))
```

## How It Works

The Universal Router contract processes a sequence of commands in a single transaction. Each command performs a specific operation, such as swapping tokens or interacting with an NFT marketplace.

- **Commands**: A byte string where each byte represents an operation to perform. The value of each byte corresponds to a specific command type defined in the `Command` enum.

- **Inputs**: A list of ABI-encoded byte strings that contain the parameters for each command. The Universal Router executes each command in sequence, using the corresponding input parameters.

The `Planner` class helps build these commands and inputs with a convenient builder pattern, handling the complex ABI encoding details behind the scenes.

## Features

- Support for all Universal Router commands:
  - Uniswap V2 and V3 swaps
  - Token transfers and approvals
  - ETH wrapping/unwrapping
  - NFT marketplace interactions
  - Permit2 operations
  - Batch command execution
- Builder pattern for easy command chaining
- Type-safe encoding of command parameters
- Handles complex encoding of command parameters automatically
