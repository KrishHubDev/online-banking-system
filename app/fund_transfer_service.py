"""Fund-transfer service for OBS: validation, CBS debit and SMS/email confirmation."""


class TransferError(Exception):
    """Raised when the core banking system does not confirm a transfer."""


class FundTransferService:
    """Create and reverse transfers; CBS and notifier are injected dependencies."""

    MAX_AMOUNT = 200000
    OTP_THRESHOLD = 5000
    MODES = ("NEFT", "IMPS", "RTGS")

    def __init__(self, core_banking, notifier):
        self._cbs = core_banking
        self._notifier = notifier
        self._transfers = {}
        self._next_id = 1

    def transfer(self, from_account, to_account, amount, mode, otp_verified=False):
        """Debit through CBS, send a confirmation and return the reference number."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be numeric")
        if mode not in self.MODES:
            raise ValueError("Mode must be NEFT, IMPS or RTGS")
        if from_account == to_account:
            raise ValueError("Source and beneficiary accounts must differ")
        if amount <= 0 or amount > self.MAX_AMOUNT:
            raise ValueError("Amount must be greater than 0 and at most 200000")
        if amount > self.OTP_THRESHOLD and not otp_verified:
            raise PermissionError("OTP verification required above INR 5000")
        if self._cbs.debit(from_account, to_account, amount) != "SUCCESS":
            raise TransferError("Transfer was not confirmed by core banking")
        reference = f"TXN{self._next_id:06d}"
        self._next_id += 1
        self._transfers[reference] = {
            "from": from_account,
            "amount": amount,
            "mode": mode,
            "status": "SUCCESS",
        }
        self._notifier.send_confirmation(reference, amount)
        return reference

    def reverse(self, reference):
        """Credit the amount back to the source account (auto-reversal)."""
        transfer = self._get(reference)
        if transfer["status"] == "REVERSED":
            raise ValueError("Transfer is already reversed")
        self._cbs.credit(transfer["from"], transfer["amount"])
        transfer["status"] = "REVERSED"

    def get_status(self, reference):
        """Return the status of a transfer."""
        return self._get(reference)["status"]

    def _get(self, reference):
        if reference not in self._transfers:
            raise KeyError(f"Unknown reference number: {reference}")
        return self._transfers[reference]
