from pyteal import *


def approval():
    
    # These addresses are only for temporary use and NOT REAL ADDRESSES
    app_address = Global.current_application_address()
    ureca_address = Addr("XDCJ64JIMQM6O2K7YZKZBOENLUALXHDNPFBQPED7KESUMDHA3ZFWLZMLEY")
    reserve_address = Addr("GTPS3JCRQJ7BNU43ZFHGYCVIITZ7E7R3WRGC25WPAFENFFA7XDZSAVDGCQ")
    
    # Creating Application
    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(0)),
            Return(Int(1))
        ]
    )

    # Creating asset within the address and configure all addresses with special permissions
    asset_creation = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetConfig,
            TxnField.config_asset_total: Int(100000000000000000),
            TxnField.config_asset_decimals: Int(3),
            TxnField.config_asset_unit_name: Bytes("ut"),
            TxnField.config_asset_name: Bytes("RecToken1"),
            TxnField.config_asset_default_frozen: Int(1),
            TxnField.config_asset_manager: ureca_address,
            TxnField.config_asset_reserve: reserve_address,
            TxnField.config_asset_clawback: app_address

        }),
        InnerTxnBuilder.Submit(),
        App.globalPut(Bytes("asset"), InnerTxn.created_asset_id()),
        Approve()
    )

    # Sending all amounts to reserve account
    # Make sure to opt in reserve acc to the asset, beforehand
    reserve = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_sender: app_address,
            TxnField.asset_receiver: reserve_address,
            TxnField.asset_amount: Int(100000000000000000),
            TxnField.xfer_asset: App.globalGet(Bytes("asset")),
        }),
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # Transferring the given amount of asset from Address A to Address B
    # Make sure all accounts have opted in, beforehand
    transfer = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_sender: Txn.accounts[1],
            TxnField.asset_receiver: Txn.accounts[2],
            TxnField.asset_amount: Btoi(Txn.application_args[1]),
            TxnField.xfer_asset: App.globalGet(Bytes("asset")),
        }),
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # Comparing 2 inputs and checking if they are within the tolerance of 2%
    tolerance = Seq(
        If(Btoi(Txn.application_args[1]) / Btoi(Txn.application_args[2]) * Int(100) <= Int(102),
        App.globalPut(Bytes("checker"), Int(1)), App.globalPut(Bytes("checker"), Int(0))),
        If(Btoi(Txn.application_args[1]) / Btoi(Txn.application_args[2]) * Int(100) <= Int(102),
        App.globalPut(Bytes("checker"), Int(1)), App.globalPut(Bytes("checker"), Int(0))))

    # Minting given amount of asset, which means taking from reserve account and putting into circulation on blockchain
    mint = Seq(
        Seq(
            tolerance,
            Assert(App.globalGet(Bytes("checker")) == Int(1)),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_sender: reserve_address,
                TxnField.asset_receiver: Txn.accounts[1],
                TxnField.asset_amount: Btoi(Txn.application_args[3]),
                TxnField.xfer_asset: App.globalGet(Bytes("asset")),
            }),
            InnerTxnBuilder.Submit(),
            Approve()
        ))

    # Retiring given amount of asset, which means taking back from address and sending to reserve account
    retire = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_sender: Txn.accounts[1],
            TxnField.asset_receiver: reserve_address,
            TxnField.asset_amount: Btoi(Txn.application_args[1]),
            TxnField.xfer_asset: App.globalGet(Bytes("asset")),
        }),
        InnerTxnBuilder.Submit(),
        Approve()
    )
    return Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(1))],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(1))],
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],
        [And(Txn.sender() == ureca_address, Txn.application_args[0] == Bytes("asset-creation")), asset_creation],
        [And(Txn.sender() == ureca_address, Txn.application_args[0] == Bytes("mint")), mint],
        [And(Txn.sender() == ureca_address, Txn.application_args[0] == Bytes("retire")), retire],
        [And(Txn.sender() == ureca_address, Txn.application_args[0] == Bytes("transfer")), transfer],
        [And(Txn.sender() == ureca_address, Txn.application_args[0] == Bytes("reserve")), reserve]

    )


def clear():
    return Return(Int(1))


if __name__ == "__main__":
    with open("approval_program.teal", "w") as f:
        compiled = compileTeal(approval(), mode=Mode.Application, version=6)
        f.write(compiled)

    with open("clear_state_program.teal", "w") as f:
        compiled = compileTeal(clear(), mode=Mode.Application, version=6)
        f.write(compiled)
