# REC project

- Download teal_python.py 
- Create project on Intellij IDEA
- Upload this file to src
- Prepare your platform (python, Purestake node, pyteal)
- Compile

Description
REC Smart Contract is a contract that automatically handles the management of our asset/REC.
The smart contract can create the asset, mint, reserve, transfer, and retire. All transactions must be called by our Creator Address (which will be URECA Address), otherwise will be rejected. Asset ID and numbers must be integers. Arguments, accounts, and assets must an array. To Test it create 4 accounts, which will represent Ureca, Reserve account, UserA, UserB

## Creating Asset Transaction
- Adjust the parameters of new asset in function asset_creation()
- Create the Smart Contract
- Fund the dApp account to process further transactions
- Call App. The argument should be: ["asset-creation"]
- Accounts: [reserve account]

## Reserving Transaction
- Reserving an asset means sending all amounts to the reserve account. Make sure to opt-in reserve acc to the asset, beforehand. Then:
- Arguments: ["reserve"]
- Assets: [(asset id)]
- Account: [(reserve account)]

## Minting Transaction
- Make the receiver opt-in to the asset
- To call the App should have these settings
- Txn Caller must be Ureca address
- Arguments: ["mint", (bigger number), (smaller), (asset amount number) ]
- Asset: (created asset id)
- Accounts: ( receiver address, reserve account)

## Transferring Transaction
- Make sure both receiver and sender have opted-in to the asset
- To call the App should have these settings
- Txn Caller must be Ureca address
- Arguments: ["transfer", (asset amount number) ]
- Asset: (created asset id)
- Accounts: (sender account, receiver account, reserve address)

## Retiring Transaction
- To call the App should have these settings
- Txn Caller must be Ureca address
- Arguments: ["retire", (asset amount number) ]
- Asset: (created asset id)
- Accounts: (sender account, reserve address)

## Deployed app 
App address: CDKTNZILMUAOFNAHMUUVVALE3F6S6ONM53HTIOZWW5HO22G2NYZHX5IZ24
Stateful smart contract ID : 204737434
Asset ID: 204737697
