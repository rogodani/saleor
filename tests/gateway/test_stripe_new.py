from decimal import Decimal
from math import isclose
import os

import pytest

from saleor.payment.gateways.stripe.utils import (
    get_amount_for_stripe,
    get_currency_for_stripe,
)
from saleor.payment.gateways.stripe_new import (
    TransactionKind,
    authorize,
    get_amount_for_stripe,
    get_currency_for_stripe,
)
from saleor.payment.interface import (
    CreditCardInfo,
    CustomerSource,
    GatewayConfig,
    TokenConfig,
)
from saleor.payment.utils import create_payment_information

TRANSACTION_AMOUNT = Decimal(42.42)
TRANSACTION_REFUND_AMOUNT = Decimal(24.24)
TRANSACTION_CURRENCY = "USD"
TRANSACTION_TOKEN = "fake-stripe-id"
FAKE_TOKEN = "pm_card_pl"
ERROR_MESSAGE = "error-message"


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
    RECORD = (
        False
    )  # Set to True if recording new cassette with sandbox using credentials in env
    connection_params = {
        "public_key": os.environ.get("STRIPE_PUBLIC_KEY", "")
        if RECORD
        else "PUBLIC_KEY",
        "secret_key": os.environ.get("STRIPE_SECRET_KEY", "")
        if RECORD
        else "SECRET_KEY",
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
    payment = stripe_payment
    payment_info = create_payment_information(payment, FAKE_TOKEN)
    response = authorize(payment_info, sandbox_gateway_config)
    assert not response.error
    assert response.kind == TransactionKind.AUTH
    assert isclose(response.amount, TRANSACTION_AMOUNT)
    assert response.currency == TRANSACTION_CURRENCY
    assert response.is_success is True
