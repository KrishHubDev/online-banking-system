def filter_transactions(transactions, account_no, txn_type=None):
    """Return transactions for an account, optionally filtered by type."""
    return [
        txn
        for txn in transactions
        if txn["account_no"] == account_no
        and (
            txn_type is None
            or txn["type"] == txn_type
        )
    ]
