from operator import sub
from tkinter import N
from brownie import Lottery, config, network, interface, VRFCoordinatorV2Mock, LinkToken
from scripts.helpful_scripts import (
    LOCAL_DEVELOPMENT_NETWORKS,
    deploy_mocks,
    get_account,
    get_contract,
    fund_with_link,
)
import time
from web3 import Web3

gasPrice = Web3.toWei(2.5, "gwei")
amount = Web3.toWei(3, "ether")

randomWords = [7878, 83776]


def deploy_lottery():
    account = get_account()
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        coordinator_mock = deploy_mocks(VRFCoordinatorV2Mock)
        creation_tx = coordinator_mock.createSubscription({"from": account})
        subID = creation_tx.events["SubscriptionCreated"]["subId"]
    else:
        subID = config["networks"][network.show_active()]["subId"]
    lottery_contract = Lottery.deploy(
        get_contract("eth_usd_price_feed"),
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        ##config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        subID,
        {"from": account, "gas_price": gasPrice},
    )
    print("deployed lottery!")
    return lottery_contract, account, subID


def start_lottery(account=None):
    if account:
        account = account
    else:
        account = get_account()
    lottery = Lottery[-1]
    tx = lottery.startLottery({"from": account, "gas_price": gasPrice})
    tx.wait(1)
    print("YAAY The lottery has started!")


def enter_lotter(account=None):
    if account:
        account = account
    else:
        account = get_account()
    lottery = Lottery[-1]
    amount = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": amount, "gas_price": gasPrice})
    tx.wait(1)
    print(f"Yaay {account} entered the lottery!")


def end_lottery(account=None):
    if account:
        account = account
    else:
        account = get_account()
    lottery = Lottery[-1]
    ##COORDINATOR = interface.VRFCoordinatorV2Interface(get_contract("vrf_coordinator"))
    ##COORDINATOR.addConsumer(686, lottery.address, {"from": account})
    ##fund_with_link(fromAddress=account,linkTokenContract=None,toAddress=lottery.address,linkAmount=Web3.toWei(0.5, "ether"),)
    ##tx = lottery.endLottery({"from": account, "gas_price": gasPrice})
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    print("HOhoo the lottery has ended...Winner Loading.....")
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        requestId = ending_tx.events["request_id"]["requestId"]
        coordinator = deploy_mocks(VRFCoordinatorV2Mock)
        fulfill_tx = coordinator.fulfillRandomWordsWithOverride(
            requestId, lottery, randomWords, {"from": account}
        )
        fulfill_tx.wait(1)
        print(f"{lottery.recent_winner()} is the new Winner!!!!")
    else:
        time.sleep(180)
        print(f"{lottery.recent_winner()} is the new Winner!!!!")


def read_data(player_index):
    lottery = Lottery[-1]
    ##noOfPlayers = len(lottery.players())
    lotteryState = lottery.lottery_state()
    ##print(f"There are {noOfPlayers} players")
    print(f"The state of the lottery is {lotteryState}")
    print(f"The recent randomness is {lottery.recent_randomness()}")
    print(f"The entrance fee is {lottery.getEntranceFee()}")
    ##print(lottery.players(player_index))
    print(f"The balance of this lottery contract is {lottery.balance()}")
    print(f"{lottery.recent_winner()} is the recent Winner!!!!")
    ##print(f"{lottery.players([0])}")


def main():
    lottery, account, subId = deploy_lottery()
    start_lottery(account)
    enter_lotter(account)
    ##enter_lotter(get_account(account_name="rastaBujo"))
    read_data(0)
    add_consumer_contract(lottery, account, subId)
    end_lottery(account)
    read_data(0)


def add_consumer_contract(contract=None, account=None, subId=None):
    if contract:
        lottery = contract
    else:
        lottery = Lottery[-1]
    if account:
        account = account
    else:
        account = get_account()
    coordinator_address = get_contract("vrf_coordinator", account)
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        coordinator = VRFCoordinatorV2Mock[-1]
        if subId:
            subId = subId
        else:
            creation_tx = coordinator.createSubscription({"from": account})
            subId = creation_tx.events["SubscriptionCreated"]["subId"]
            return creation_tx
        funding_tx = coordinator.fundSubscription(subId, amount, {"from": account})
        funding_tx.wait(1)
        if coordinator.consumerIsAdded(subId, lottery) == True:
            print("Contract already added in consumers list")
        else:
            adding_tx = coordinator.addConsumer(subId, lottery, {"from": account})
            adding_tx.wait(1)
            print("Contract added to consumers list>>")
    else:
        coordinator = interface.VRFCoordinatorV2Interface(coordinator_address)
        coordinator.addConsumer(
            686, lottery.address, {"from": account, "gas_price": gasPrice}
        )
        print("Contract added to Consumers list successfully....")
