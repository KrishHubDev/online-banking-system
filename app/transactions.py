def filter_transactions(
    transactions, account_no, start_date, end_date, txn_type=None
):
    """Filter transactions by account, date range, and optional type."""
    return [
        txn
        for txn in transactions
        if txn["account_no"] == account_no
        and start_date <= txn["date"] <= end_date
        and (
            txn_type is None
            or txn["type"] == txn_type
        )
    ]
