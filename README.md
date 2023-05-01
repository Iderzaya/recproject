# REC project

The REC Smart Contract is a program written in Pyteal, a language developed by Algorand. It manages our asset/REC automatically by creating it, minting, reserving, transferring, and retiring it. Only our Creator Address (URECA Address) is allowed to initiate these transactions, otherwise they will be rejected. All asset IDs and numbers must be integers, while arguments, accounts, and assets must be in the form of an array. 


## Getting Started

- Create project on Intellij IDEA (not mandatory, but this is an very easy tool I used for my development). [Tutorial here](https://developer.algorand.org/articles/making-development-easier-algodea-intellij-plugin/)
- Prepare your platform (install python, create account on Purestake node, install pyteal)
- Download teal.py from src files
- Upload this file in src folder of Intellij IDEA project
- Create 4 accounts representing Ureca, Reserve account, Producer account, and Buyer's account. This can be done on Intellij IDEA

## Deploying your smart contract
- To create a smart contract, you must first customize the settings of the new asset in the asset_creation() function, including its name and default accounts. It is important to note that certain parameters cannot be modified after deployment.
- Create the Smart Contract If you are using Intellij, folllow the [tutorial](https://developer.algorand.org/articles/making-development-easier-algodea-intellij-plugin/). Or you can also create an application using algorand sdk's simple transaction. It is important to ensure that the transaction is sent from the Ureca address.
- Once the smart contract has been successfully created, it is necessary to fund its account in order to enable further transactions. If you are using testnet, fund [here](https://bank.testnet.algorand.network/)

## Actions Smart Contract perform on ASA(Algorand Standart Asset)
All these instances must be called by Ureca Address(aka the creator of the smart contract, else they will be rejected)

### Creating Asset Transaction

In teal.py file, by default you will be creating an asset with following settings: 


```sh
InnerTxnBuilder.SetFields({
        TxnField.type_enum: TxnType.AssetConfig,
        TxnField.fee: Global.min_txn_fee(),
        TxnField.config_asset_total: Int(100000000000000000),
        TxnField.config_asset_decimals: Int(0),
        TxnField.config_asset_unit_name: Bytes("rec"),
        TxnField.config_asset_name: Bytes("RecToken2504"),
        TxnField.config_asset_default_frozen: Int(1),
        TxnField.config_asset_manager: App.globalGet(Bytes("Creator")),
        TxnField.config_asset_reserve: Txn.accounts[1],
        TxnField.config_asset_clawback: Global.current_application_address()
}),
```


Calling smart contract to create asset, transactions necessary additional parameters are:
- Arguments array: "asset-creation"
- Accounts array: [(reserveAccount)]


### Reserving Transaction

Make sure to opt-in reserve acc to the asset, beforehand. Reserving an asset means sending all amounts to the reserve account.
Calling smart contract to reserve the asset, transactions necessary additional parameters are:

- Arguments array: "reserve"
- Foreign Assets: assetId
- Accounts array: reserveAccount

### Minting Transaction

Make sure Producer's Account has opted-in to the asset.
Calling smart contract to mint the asset, transactions necessary additional parameters are:

- Arguments array: "mint", biggerNumber, smallerNumber, tolerancePercentage, assetAmount
- Foreign Assets array: assetId
- Accounts array:  producerAccount, reserveAccount

### Transferring Transaction

Make sure Buyer's Account have opted-in to the asset
Calling smart contract to transfer the asset, transactions necessary additional parameters are:

- Arguments array: "transfer", assetAmount
- Foreign Assets array: assetId
- Accounts array: producerAccount, buyerAccount, reserveAccount

### Retiring Transaction
Calling smart contract to retire the asset, transactions necessary additional parameters are:

- Arguments array: "retire", assetAmount 
- Foreign Assets array: assetId
- Accounts array: buyerAccount, reserveAccount

### Already deployed application for testing

Stateful smart contract ID : 207608481
Asset ID: 207610354
