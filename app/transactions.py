def filter_transactions(transactions, account_no):
    """Return transactions for an account."""
    return [
        txn
        for txn in transactions
        if txn["account_no"] == account_no
    ]
