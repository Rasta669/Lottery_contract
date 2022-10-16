from brownie import network, interface, Lottery
from scripts.deploy_lottery import (
    deploy_lottery,
    end_lottery,
    enter_lotter,
    start_lottery,
    add_consumer_contract,
)
from scripts.helpful_scripts import (
    LOCAL_DEVELOPMENT_NETWORKS,
    fund_with_link,
    get_account,
    get_contract,
)
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    start_lottery()
    enter_lotter(account)
    add_consumer_contract(lottery)
    end_lottery()
    ##tx = lottery.startLottery({"from": account})
    ##tx.wait(1)
    ##lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    ##fund_with_link(account, None, lottery.address, 1000000000000000000)
    ##coordinator = interface.VRFCoordinatorV2Interface(get_contract("vrf_coordinator").address) for vrfv2
    ##coordinator.addConsumer(686, lottery.address, {"from": account})
    ##lottery.endLottery({"from": account})
    ##time.sleep(180)
    assert lottery.recent_winner() == account
    assert lottery.balance() == 890000000
