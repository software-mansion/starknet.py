def _replace_invoke_contract_address_with_sender_address(data: dict):
    data["sender_address"] = data.get("sender_address") or data.get("contract_address")

    if data["sender_address"] is None:
        raise ValueError(
            "Missing field `contract_address` or `sender_address` for InvokeTransactionSchema."
        )

    del data["contract_address"]
