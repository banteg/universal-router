import pytest
from uniswap.universal_router import Command, Planner

dev = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
amount = 10**18


def test_planner():
    planner = Planner()
    planner.add(Command.WRAP_ETH, dev, amount)
    planner.add(Command.UNWRAP_WETH, dev, amount)
    print(planner)
    commands, inputs = planner.build()
    assert commands == bytes.fromhex("0b0c")
    assert inputs == [
        bytes.fromhex(
            "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a7640000"
        ),
        bytes.fromhex(
            "000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb922660000000000000000000000000000000000000000000000000de0b6b3a7640000"
        ),
    ]


def test_revert():
    planner = Planner()
    with pytest.raises(ValueError, match="WRAP_ETH cannot be allowed to revert"):
        planner.add(Command.WRAP_ETH, dev, amount, allow_revert=True)
