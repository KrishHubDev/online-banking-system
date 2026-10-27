"""Demonstration of app/transactions.py using synthetic transaction records."""
from app.transactions import filter_transactions

TRANSACTIONS = [
    {"ref": "TXN001", "account_no": "ACC1001", "date": "2026-08-05", "type": "IMPS", "amount": 2500},
    {"ref": "TXN002", "account_no": "ACC1001", "date": "2026-08-12", "type": "NEFT", "amount": 12000},
    {"ref": "TXN003", "account_no": "ACC1001", "date": "2026-09-02", "type": "IMPS", "amount": 800},
    {"ref": "TXN004", "account_no": "ACC2002", "date": "2026-08-07", "type": "RTGS", "amount": 250000},
]

def refs(result):
    return [txn["ref"] for txn in result]

CHECKS = [
    ("Account + August, no type filter", refs(filter_transactions(TRANSACTIONS, "ACC1001", "2026-08-01", "2026-08-31")), ["TXN001", "TXN002"]),
    ("Account + August, IMPS only", refs(filter_transactions(TRANSACTIONS, "ACC1001", "2026-08-01", "2026-08-31", "IMPS")), ["TXN001"]),
    ("Account + September, IMPS only", refs(filter_transactions(TRANSACTIONS, "ACC1001", "2026-09-01", "2026-09-30", "IMPS")), ["TXN003"]),
    ("Type not used in range (RTGS)", refs(filter_transactions(TRANSACTIONS, "ACC1001", "2026-08-01", "2026-08-31", "RTGS")), []),
    ("Unknown account", refs(filter_transactions(TRANSACTIONS, "ACC9999", "2026-08-01", "2026-09-30")), []),
    ("Empty transaction list", refs(filter_transactions([], "ACC1001", "2026-08-01", "2026-08-31")), []),
]

passed = 0
for name, actual, expected in CHECKS:
    ok = actual == expected
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}: {name} -> {actual}")
print(f"{'PASS' if passed == len(CHECKS) else 'FAIL'}: {passed}/{len(CHECKS)} demonstration checks passed.")
