def replace_invoke_sender_address_with_contract_address(data: dict):
    data["contract_address"] = data.get("contract_address") or data.get(
        "sender_address"
    )

    if data["contract_address"] is None:
        raise ValueError(
            "Missing field `contract_address` or `sender_address` for InvokeTransactionSchema."
        )

    del data["sender_address"]
