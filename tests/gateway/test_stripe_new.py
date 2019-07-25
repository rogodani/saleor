from decimal import Decimal
import pytest

from saleor.payment.gateways.stripe_new import authorize
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
FAKE_TOKEN = "fake-token"
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
    connection_params = {
        "public_key": "STRIPE_PUBLIC_KEY",
        "secret_key": "STRIPE_SECRET",
    }
    gateway_config.connection_params.update(connection_params)
    return gateway_config


@pytest.fixture()
def stripe_payment(payment_dummy):
    payment_dummy.total = TRANSACTION_AMOUNT
    payment_dummy.currency = TRANSACTION_CURRENCY
    return payment_dummy


@pytest.fixture
def simple_token():
    return ""


@pytest.mark.integration
@pytest.mark.vcr(filter_headers=["authorization"])
def test_auhorize(gateway_config, stripe_payment):
    payment = stripe_payment
    payment_info = create_payment_information(payment, FAKE_TOKEN)
    authorize(payment_info, gateway_config)
