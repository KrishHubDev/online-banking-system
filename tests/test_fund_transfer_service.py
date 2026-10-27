"""Unit tests for FundTransferService with CBS and notifier replaced by mocks."""
from unittest.mock import Mock

import pytest

from app.fund_transfer_service import FundTransferService, TransferError


@pytest.fixture
def cbs():
    """A mock core banking system that approves every debit by default."""
    mock = Mock(spec=["debit", "credit"])
    mock.debit.return_value = "SUCCESS"
    return mock


@pytest.fixture
def notifier():
    """A mock SMS/email gateway."""
    return Mock(spec=["send_confirmation"])


@pytest.fixture
def service(cbs, notifier):
    svc = FundTransferService(cbs, notifier)
    yield svc                 # test runs here
    cbs.reset_mock()          # teardown: clear recorded calls
    notifier.reset_mock()


# ---------- positive cases ----------

def test_transfer_returns_first_reference_and_debits_amount(service, cbs):
    assert service.transfer("ACC1", "ACC2", 2000, "IMPS") == "TXN000001"
    cbs.debit.assert_called_once_with("ACC1", "ACC2", 2000)


def test_reference_numbers_increase(service):
    assert service.transfer("ACC1", "ACC2", 100, "NEFT") == "TXN000001"
    assert service.transfer("ACC1", "ACC2", 100, "NEFT") == "TXN000002"


def test_successful_transfer_sends_confirmation(service, notifier):
    reference = service.transfer("ACC1", "ACC2", 1500, "IMPS")
    notifier.send_confirmation.assert_called_once_with(reference, 1500)
    assert service.get_status(reference) == "SUCCESS"


@pytest.mark.parametrize("amount", [1, 5000])  # no OTP needed up to the threshold
def test_amounts_up_to_otp_threshold_need_no_otp(service, amount):
    assert service.transfer("ACC1", "ACC2", amount, "IMPS") == "TXN000001"


@pytest.mark.parametrize("amount", [5001, 200000])  # OTP needed above the threshold
def test_amounts_above_threshold_succeed_with_otp(service, amount):
    assert service.transfer("ACC1", "ACC2", amount, "RTGS", otp_verified=True) == "TXN000001"


# ---------- negative / exception cases ----------

@pytest.mark.parametrize("amount", [0, -1, 200001])  # just outside the valid range
def test_out_of_range_amounts_are_rejected(service, cbs, amount):
    with pytest.raises(ValueError, match="greater than 0"):
        service.transfer("ACC1", "ACC2", amount, "IMPS", otp_verified=True)
    cbs.debit.assert_not_called()


def test_amount_above_threshold_without_otp_is_rejected(service, cbs):
    with pytest.raises(PermissionError, match="OTP"):
        service.transfer("ACC1", "ACC2", 5001, "IMPS")
    cbs.debit.assert_not_called()


@pytest.mark.parametrize("amount", ["2000", None, True])
def test_non_numeric_amount_raises_type_error(service, amount):
    with pytest.raises(TypeError):
        service.transfer("ACC1", "ACC2", amount, "IMPS")


def test_invalid_mode_is_rejected(service, cbs):
    with pytest.raises(ValueError, match="NEFT, IMPS or RTGS"):
        service.transfer("ACC1", "ACC2", 100, "UPI")
    cbs.debit.assert_not_called()


def test_same_source_and_beneficiary_is_rejected(service, cbs):
    with pytest.raises(ValueError, match="must differ"):
        service.transfer("ACC1", "ACC1", 100, "IMPS")
    cbs.debit.assert_not_called()


def test_declined_debit_raises_transfer_error_and_stores_nothing(service, cbs, notifier):
    cbs.debit.return_value = "FAILED"
    with pytest.raises(TransferError):
        service.transfer("ACC1", "ACC2", 500, "IMPS")
    notifier.send_confirmation.assert_not_called()
    with pytest.raises(KeyError):
        service.get_status("TXN000001")


def test_cbs_outage_propagates_and_stores_nothing(service, cbs, notifier):
    cbs.debit.side_effect = ConnectionError("CBS down")
    with pytest.raises(ConnectionError):
        service.transfer("ACC1", "ACC2", 500, "IMPS")
    notifier.send_confirmation.assert_not_called()
    with pytest.raises(KeyError):
        service.get_status("TXN000001")


def test_unknown_reference_raises_key_error(service):
    with pytest.raises(KeyError):
        service.get_status("TXN999999")


# ---------- reversal ----------

def test_reverse_credits_amount_and_marks_reversed(service, cbs):
    reference = service.transfer("ACC1", "ACC2", 2000, "IMPS")
    service.reverse(reference)
    cbs.credit.assert_called_once_with("ACC1", 2000)
    assert service.get_status(reference) == "REVERSED"


def test_reversing_twice_is_rejected_and_credits_once(service, cbs):
    reference = service.transfer("ACC1", "ACC2", 500, "IMPS")
    service.reverse(reference)
    with pytest.raises(ValueError, match="already reversed"):
        service.reverse(reference)
    cbs.credit.assert_called_once_with("ACC1", 500)


def test_reverse_unknown_reference_raises_key_error(service):
    with pytest.raises(KeyError):
        service.reverse("TXN000042")


def test_failed_credit_leaves_transfer_successful(service, cbs):
    reference = service.transfer("ACC1", "ACC2", 500, "IMPS")
    cbs.credit.side_effect = ConnectionError("credit failed")
    with pytest.raises(ConnectionError):
        service.reverse(reference)
    assert service.get_status(reference) == "SUCCESS"
