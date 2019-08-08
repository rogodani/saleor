from decimal import Decimal
from math import isclose
import os

import pytest

from saleor.payment.gateways.stripe_new import TransactionKind, authorize
from saleor.payment.interface import GatewayConfig
from saleor.payment.utils import create_payment_information

TRANSACTION_AMOUNT = Decimal(42.42)
TRANSACTION_REFUND_AMOUNT = Decimal(24.24)
TRANSACTION_CURRENCY = "USD"
PAYMENT_METHOD_CARD_SIMPLE = "pm_card_pl"

# Set to True if recording new cassette with sandbox using credentials in env
RECORD = False


@pytest.fixture()
def gateway_config():
    return GatewayConfig(
        gateway_name="stripe_new",
        auto_capture=False,
        template_path="template.html",
        connection_params={
            "public_key": "public",
            "secret_key": "secret",
            "store_name": "Saleor",
            "store_image": "image.gif",
            "prefill": True,
            "remember_me": True,
            "locale": "auto",
            "enable_billing_address": False,
            "enable_shipping_address": False,
        },
    )


@pytest.fixture()
def sandbox_gateway_config(gateway_config):
    if RECORD:
        connection_params = {
            "public_key": os.environ.get("STRIPE_PUBLIC_KEY"),
            "secret_key": os.environ.get("STRIPE_SECRET_KEY"),
        }
        gateway_config.connection_params.update(connection_params)
    return gateway_config


@pytest.fixture()
def stripe_payment(payment_dummy):
    payment_dummy.total = TRANSACTION_AMOUNT
    payment_dummy.currency = TRANSACTION_CURRENCY
    return payment_dummy


@pytest.mark.integration
@pytest.mark.vcr(filter_headers=["authorization"])
def test_authorize(sandbox_gateway_config, stripe_payment):
    payment_info = create_payment_information(
        stripe_payment, PAYMENT_METHOD_CARD_SIMPLE
    )
    response = authorize(payment_info, sandbox_gateway_config)
    assert not response.error
    assert response.kind == TransactionKind.AUTH
    assert isclose(response.amount, TRANSACTION_AMOUNT)
    assert response.currency == TRANSACTION_CURRENCY
    assert response.is_success is True


@pytest.mark.integration
@pytest.mark.vcr(filter_headers=["authorization"])
def test_authorize_error_response(stripe_payment, sandbox_gateway_config):
    INVALID_METHOD = "abcdefghijklmnoprstquwz"
    payment_info = create_payment_information(stripe_payment, INVALID_METHOD)
    response = authorize(payment_info, sandbox_gateway_config)

    assert response.error == "No such payment_method: " + INVALID_METHOD
    assert response.transaction_id == INVALID_METHOD
    assert response.kind == TransactionKind.AUTH
    assert not response.is_success
    assert response.amount == stripe_payment.total
    assert response.currency == stripe_payment.currency
