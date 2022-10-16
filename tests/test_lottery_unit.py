from brownie import exceptions, VRFCoordinatorMock, network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_DEVELOPMENT_NETWORKS,
    get_account,
    fund_with_link,
)
from web3 import Web3
import pytest
import time


def test_get_Entrance_Fee():
    if network.show_active() not in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    assert lottery.getEntranceFee() == Web3.toWei(0.025, "ether")


def test_cant_enter_if_not_started():
    if network.show_active() not in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": lottery.getEntranceFee()})


def test_can_enter_if_started():
    if network.show_active() not in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lotter():
    if network.show_active() not in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(
        fromAddress=account,
        linkTokenContract=None,
        toAddress=lottery.address,
        linkAmount=2000000000000000000000,
    )
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_get_winner():
    if network.show_active() not in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(
        fromAddress=account,
        linkTokenContract=None,
        toAddress=lottery.address,
        linkAmount=2000000000000000000000,
    )
    tx1 = lottery.endLottery({"from": account})
    tx1.wait(1)
    time.sleep(60)
    requestId = tx1.events["request_id"]["requestId"]
    Rand = 619
    VRFCoordinatorMock[-1].callBackWithRandomness(
        requestId, Rand, lottery.address, {"from": account}
    )
    assert lottery.recent_winner() == account
