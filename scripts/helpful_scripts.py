from email.headerregistry import Address
import re
from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorV2Mock,
    LinkToken,
    interface,
)
from web3 import Web3

LOCAL_DEVELOPMENT_NETWORKS = ["development", "local-ganache"]
FORKED_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
DECIMALS = 8
STARTING_PRICE = 200000000000
gasPrice = Web3.toWei(2.5, "gwei")


def get_account(index=None, account_name=None):
    if index:
        return accounts[index]
    if account_name:
        return accounts.load(account_name)
    if (
        network.show_active() in LOCAL_DEVELOPMENT_NETWORKS
        or network.show_active() in FORKED_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name, account=None):
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        if account:
            account = account
        else:
            account = get_account()
        contract_to_mock = {
            "eth_usd_price_feed": MockV3Aggregator,
            "vrf_coordinator": VRFCoordinatorV2Mock,
            "link_token": LinkToken,
        }
        contract_type = contract_to_mock[contract_name]
        if len(contract_type) <= 0:
            deployed_contract = deploy_mocks(
                contract_type,
                DECIMALS=DECIMALS,
                STARTING_PRICE=STARTING_PRICE,
                account=account,
            )
            contract_address = deployed_contract.address
            ##contract = Contract.from_abi(_name=contract_object.name,address=contract_address,abi=contract_object.abi,)
        else:
            contract_object = contract_type[-1]
            contract_address = contract_object.address
            # contract = Contract.from_abi(_name=contract_object.name,address=contract_address,abi=contract_object.abi,)
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        ##aggregator_contract = interface.AggregatorV3Interface(contract_address)
        ##vrf_contract = interface.VRFCoordinatorV2Interface(contract_address)
        ##link_contract = interface.LinkTokenInterface(contract_address)
        ##contract_to_contract = {"eth_usd_price_feed": aggregator_contract,"vrf_coordinator": vrf_contract,"link_token": link_contract,}
        ##contract = contract_to_contract[contract_name]
    return contract_address


def deploy_mocks(contract, DECIMALS=None, STARTING_PRICE=None, account=None):
    if account:
        account = account
    else:
        account = get_account()
    if len(contract) > 0:
        return contract[-1]
    if contract == MockV3Aggregator:
        mock_aggregator = MockV3Aggregator.deploy(
            DECIMALS, STARTING_PRICE, {"from": account}
        )
        print("MockV3Aggregator deployed!")
        return mock_aggregator
    if contract == LinkToken:
        link_token = LinkToken.deploy({"from": account})
        print("link mock deployed!")
        return link_token
    if contract == VRFCoordinatorV2Mock:
        link_token = deploy_mocks(contract=LinkToken)
        mock_coordinator = VRFCoordinatorV2Mock.deploy(
            config["networks"][network.show_active()]["fee"],
            gasPrice,
            {"from": account},
        )
        print("vrf-coordinatorMock deployed!")
        return mock_coordinator


def fund_with_link(
    fromAddress,
    linkTokenContract,
    toAddress,
    linkAmount,
):
    if fromAddress:
        fromAddress = fromAddress
    else:
        fromAddress = get_account()

    if linkTokenContract:
        linkTokenContract.transfer(toAddress, linkAmount, {"from": fromAddress})
    else:
        linktoken_address = get_contract("link_token")
        if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
            linktoken = deploy_mocks("link_token", account=fromAddress)
        else:
            linktoken = interface.LinkTokenInterface(linktoken_address)
        tx = linktoken.transfer(toAddress, linkAmount, {"from": fromAddress})
        tx.wait(1)
    print("Lottery Contract funded with link!")
