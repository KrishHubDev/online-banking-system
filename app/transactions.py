def filter_transactions(transactions, account_no, start_date, end_date):
    """Return transactions for an account within a date range."""
    return [
        txn
        for txn in transactions
        if txn["account_no"] == account_no
        and start_date <= txn["date"] <= end_date
    ]