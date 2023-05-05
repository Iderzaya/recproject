from pyteal import *


def approval():
    reserve_address = App.globalGet(Bytes("Reserve"))

    # Creating Application
    def on_creation():
        return Seq(
            [
                Assert(
                    And(
                        Txn.application_args.length() == Int(0),
                        Txn.type_enum() == TxnType.ApplicationCall,
                        Txn.fee() == Global.min_txn_fee(),
                        Txn.close_remainder_to() == Global.zero_address(),
                        Txn.rekey_to() == Global.zero_address(),
                        Global.group_size() == Int(1)
                    )),
                App.globalPut(Bytes("asset"), Int(0)),
                Return(Int(1))
            ]
        )

    def deleteorupdate():
        return Reject()

    # Creating asset within the address and configure all addresses with special permissions
    def asset_creation():
        return Seq(
            Assert(App.globalGet(Bytes("asset")) == Int(0)),
            Assert(
                And(
                    Global.creator_address() == Txn.sender(),
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.application_id() == Global.current_application_id(),
                    Global.group_size() == Int(1))
            ),
            Assert(
                Txn.fee() >= Global.min_txn_fee() * Int(2),
            ),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                # TxnField.fee: Global.min_txn_fee(),
                TxnField.fee: Int(0),
                TxnField.config_asset_total: Int(100000000000000000),
                TxnField.config_asset_decimals: Int(4),
                TxnField.config_asset_unit_name: Bytes("rec"),
                TxnField.config_asset_name: Bytes("RecAsset0305"),
                TxnField.config_asset_default_frozen: Int(1),
                TxnField.config_asset_manager: Global.creator_address(),
                TxnField.config_asset_reserve: Txn.accounts[1],
                TxnField.config_asset_clawback: Global.current_application_address()
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(Bytes("asset"), InnerTxn.created_asset_id()),
            App.globalPut(Bytes("Reserve"), Txn.accounts[1]),
            Approve()
        )

    # Sending all amounts to reserve account
    # Make sure to opt in reserve acc to the asset, beforehand
    def reserve():
        return Seq(
            Assert(And(
                Global.creator_address() == Txn.sender(),
                Txn.application_id() == Global.current_application_id(),
                Txn.close_remainder_to() == Global.zero_address(),
                Txn.asset_close_to() == Global.zero_address(),
                Txn.accounts[1] == App.globalGet(Bytes("Reserve")),
                Txn.assets[0] == App.globalGet(Bytes("asset")),
                Txn.type_enum() == TxnType.ApplicationCall,
                Txn.on_completion() == OnComplete.NoOp,
                Global.group_size() == Int(1),
                Txn.fee() >= Global.min_txn_fee() * Int(2),
                Txn.rekey_to() == Global.zero_address(),
            )),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.asset_sender: Global.current_application_address(),
                TxnField.asset_receiver: reserve_address,
                TxnField.asset_amount: Int(100000000000000000),
                TxnField.xfer_asset: App.globalGet(Bytes("asset")),
            }),
            InnerTxnBuilder.Submit(),
            Approve()
        )

    def tol():
        return (Btoi(Txn.application_args[1]) - Btoi(Txn.application_args[2])) * Int(100) <= Btoi(
            Txn.application_args[3]) * Btoi(Txn.application_args[1])

    # Minting given amount of asset, which means taking from reserve account and putting into circulation on blockchain
    def mint():
        return Seq(
            Assert(
                And(
                    Global.creator_address() == Txn.sender(),
                    Global.group_size() == Int(1),
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.application_id() == Global.current_application_id(),
                    Txn.close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.assets[0] == App.globalGet(Bytes("asset")),
                    Txn.accounts[2] == App.globalGet(Bytes("Reserve")),
                    Btoi(Txn.application_args[1]) > Int(0),
                    Btoi(Txn.application_args[2]) > Int(0),
                    Btoi(Txn.application_args[3]) > Int(0),
                    Btoi(Txn.application_args[4]) > Int(0),
                    Btoi(Txn.application_args[1]) >= Btoi(Txn.application_args[2])
                )
            ),
            Assert(
                Txn.fee() >= Global.min_txn_fee() * Int(2),
            ),
            Assert(tol() == Int(1)),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.asset_sender: reserve_address,
                TxnField.asset_receiver: Txn.accounts[1],
                TxnField.asset_amount: Btoi(Txn.application_args[4]),
                TxnField.xfer_asset: App.globalGet(Bytes("asset")),
            }),
            InnerTxnBuilder.Submit(),
            Approve()
        )

    # Transferring the given amount of asset from Address A to Address B
    # Make sure all accounts have opted in, beforehand
    def transfer():
        return Seq(
            Assert(
                And(
                    Global.creator_address() == Txn.sender(),
                    Global.group_size() == Int(1),
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.application_id() == Global.current_application_id(),
                    Txn.assets[0] == App.globalGet(Bytes("asset")),
                    Txn.accounts[3] == App.globalGet(Bytes("Reserve")),
                    Btoi(Txn.application_args[1]) > Int(0))
            ),
            Assert(
                Txn.fee() >= Global.min_txn_fee() * Int(2),
            ),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.asset_sender: Txn.accounts[1],
                TxnField.asset_receiver: Txn.accounts[2],
                TxnField.asset_amount: Btoi(Txn.application_args[1]),
                TxnField.xfer_asset: Txn.assets[0],
            }),
            InnerTxnBuilder.Submit(),
            Approve()
        )

    # Retiring given amount of asset, which means taking back from address and sending to reserve account
    def retire():
        return Seq(
            Assert(
                And(
                    Global.creator_address() == Txn.sender(),
                    Global.group_size() == Int(1),
                    Txn.application_id() == Global.current_application_id(),
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.assets[0] == App.globalGet(Bytes("asset")),
                    Txn.accounts[2] == App.globalGet(Bytes("Reserve")),
                    Btoi(Txn.application_args[1]) > Int(0)
                )),
            Assert(
                Txn.fee() >= Global.min_txn_fee() * Int(2),
            ),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.asset_sender: Txn.accounts[1],
                TxnField.asset_receiver: reserve_address,
                TxnField.asset_amount: Btoi(Txn.application_args[1]),
                TxnField.xfer_asset: App.globalGet(Bytes("asset")),
            }),
            InnerTxnBuilder.Submit(),
            Approve()
        )

    return Cond(
        [Txn.application_id() == Int(0), on_creation()],
        [Txn.on_completion() == OnComplete.DeleteApplication, deleteorupdate()],
        [Txn.on_completion() == OnComplete.UpdateApplication, deleteorupdate()],
        [Txn.on_completion() == OnComplete.CloseOut, deleteorupdate()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.application_args[0] == Bytes("asset-creation"), asset_creation()],
        [Txn.application_args[0] == Bytes("mint"), mint()],
        [Txn.application_args[0] == Bytes("retire"), retire()],
        [Txn.application_args[0] == Bytes("transfer"), transfer()],
        [Txn.application_args[0] == Bytes("reserve"), reserve()]

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
