"""
Patron Strategy para integracion de pasarelas de pago.
Soporta: Mercado Pago, Wompi, PayPal.
"""

from abc import ABC, abstractmethod
import json
import logging
import os
from decimal import Decimal
from django.urls import reverse

logger = logging.getLogger(__name__)


class PagoResultado:
    def __init__(self, exito=False, transaction_id='', mensaje='', redirect_url='', raw_response=None):
        self.exito = exito
        self.transaction_id = transaction_id
        self.mensaje = mensaje
        self.redirect_url = redirect_url
        self.raw_response = raw_response or {}


class IPaymentGateway(ABC):
    @abstractmethod
    def crear_pago(self, factura, request) -> PagoResultado:
        pass

    @abstractmethod
    def verificar_pago(self, transaction_id) -> PagoResultado:
        pass

    @abstractmethod
    def reembolsar(self, transaction_id, monto=None) -> PagoResultado:
        pass


class MercadoPagoGateway(IPaymentGateway):
    def __init__(self):
        self.access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')
        self.public_key = os.environ.get('MERCADOPAGO_PUBLIC_KEY', '')

    def crear_pago(self, factura, request):
        try:
            import mercadopago
            sdk = mercadopago.SDK(self.access_token)
            preference_data = {
                "items": [
                    {
                        "id": str(factura.id_factura),
                        "title": f"Factura AgroSFT #{factura.id_factura}",
                        "quantity": 1,
                        "unit_price": float(factura.total),
                        "currency_id": "COP",
                    }
                ],
                "payer": {
                    "email": factura.usuario.correo,
                    "name": factura.usuario.nombres,
                    "surname": factura.usuario.apellidos,
                },
                "back_urls": {
                    "success": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['mercadopago'])),
                    "failure": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['mercadopago'])),
                    "pending": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['mercadopago'])),
                },
                "auto_return": "approved",
                "notification_url": request.build_absolute_uri(reverse('facturacion:webhook_pago', args=['mercadopago'])),
                "external_reference": str(factura.id_factura),
            }
            result = sdk.preference().create(preference_data)
            if result["status"] in (200, 201):
                data = result["response"]
                return PagoResultado(
                    exito=True,
                    transaction_id=data["id"],
                    mensaje="Preferencia creada en Mercado Pago",
                    redirect_url=data["init_point"],
                    raw_response=data,
                )
            return PagoResultado(exito=False, mensaje=f"Error MP: {result.get('status', 'desconocido')}")
        except ImportError:
            logger.warning("mercadopago SDK no instalado. pip install mercadopago")
            return PagoResultado(exito=False, mensaje="SDK Mercado Pago no disponible")
        except Exception as e:
            logger.exception("Error en MercadoPagoGateway.crear_pago")
            return PagoResultado(exito=False, mensaje=str(e))

    def verificar_pago(self, transaction_id):
        try:
            import mercadopago
            sdk = mercadopago.SDK(self.access_token)
            result = sdk.payment().get(transaction_id)
            if result["status"] == 200:
                data = result["response"]
                estado = data.get("status")
                exito = estado == "approved"
                return PagoResultado(
                    exito=exito,
                    transaction_id=transaction_id,
                    mensaje=f"Pago {estado}",
                    raw_response=data,
                )
            return PagoResultado(exito=False, mensaje="No se pudo verificar")
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))

    def reembolsar(self, transaction_id, monto=None):
        try:
            import mercadopago
            sdk = mercadopago.SDK(self.access_token)
            data = {}
            if monto:
                data["amount"] = float(monto)
            result = sdk.payment().refund(transaction_id, **data)
            exito = result["status"] in (200, 201)
            return PagoResultado(
                exito=exito,
                transaction_id=transaction_id,
                mensaje="Reembolso exitoso" if exito else "Error en reembolso",
            )
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))


class WompiGateway(IPaymentGateway):
    def __init__(self):
        self.public_key = os.environ.get('WOMPI_PUBLIC_KEY', '')
        self.private_key = os.environ.get('WOMPI_PRIVATE_KEY', '')
        self.events_key = os.environ.get('WOMPI_EVENTS_KEY', '')
        self.base_url = "https://sandbox.wompi.co/v1" if os.environ.get('WOMPI_SANDBOX', 'True') == 'True' else "https://production.wompi.co/v1"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.private_key}",
            "Content-Type": "application/json",
        }

    def crear_pago(self, factura, request):
        try:
            import requests
            payload = {
                "amount_in_cents": int(factura.total * 100),
                "currency": "COP",
                "reference": f"AGROSFT-{factura.id_factura}-{factura.usuario.id_users}",
                "customer_email": factura.usuario.correo,
                "customer_full_name": factura.usuario.get_full_name(),
                "payment_method": None,
                "redirect_url": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['wompi'])),
                "confirmation_url": request.build_absolute_uri(reverse('facturacion:webhook_pago', args=['wompi'])),
            }
            resp = requests.post(f"{self.base_url}/transactions", json=payload, headers=self._headers(), timeout=30)
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("data"):
                txn = data["data"]
                return PagoResultado(
                    exito=True,
                    transaction_id=txn["id"],
                    mensaje="Transaccion creada en Wompi",
                    redirect_url=txn.get("payment_method", {}).get("extra", {}).get("async_payment_url")
                                  or txn.get("payment_link"),
                    raw_response=txn,
                )
            return PagoResultado(exito=False, mensaje=f"Error Wompi: {data.get('error', {}).get('messages', 'desconocido')}")
        except ImportError:
            return PagoResultado(exito=False, mensaje="requests no instalado")
        except Exception as e:
            logger.exception("Error en WompiGateway.crear_pago")
            return PagoResultado(exito=False, mensaje=str(e))

    def verificar_pago(self, transaction_id):
        try:
            import requests
            resp = requests.get(f"{self.base_url}/transactions/{transaction_id}", headers=self._headers(), timeout=30)
            data = resp.json()
            if resp.status_code == 200 and data.get("data"):
                txn = data["data"]
                estado = txn["status"]
                exito = estado in ("APPROVED",)
                return PagoResultado(exito=exito, transaction_id=transaction_id, mensaje=f"Pago {estado}", raw_response=txn)
            return PagoResultado(exito=False, mensaje="No se pudo verificar")
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))

    def reembolsar(self, transaction_id, monto=None):
        try:
            import requests
            payload = {"amount_in_cents": int(monto * 100) if monto else None}
            resp = requests.post(f"{self.base_url}/transactions/{transaction_id}/refund", json=payload, headers=self._headers(), timeout=30)
            exito = resp.status_code in (200, 201)
            return PagoResultado(exito=exito, transaction_id=transaction_id, mensaje="Reembolso exitoso" if exito else "Error")
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))


class PayPalGateway(IPaymentGateway):
    def __init__(self):
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        self.client_secret = os.environ.get('PAYPAL_CLIENT_SECRET', '')
        self.sandbox = os.environ.get('PAYPAL_SANDBOX', 'True') == 'True'
        self.base_url = "https://api-m.sandbox.paypal.com" if self.sandbox else "https://api-m.paypal.com"

    def _get_token(self):
        import requests
        resp = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret),
            timeout=30,
        )
        return resp.json().get("access_token", "")

    def crear_pago(self, factura, request):
        try:
            import requests
            token = self._get_token()
            if not token:
                return PagoResultado(exito=False, mensaje="No se pudo autenticar con PayPal")
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": str(factura.id_factura),
                        "description": f"Factura AgroSFT #{factura.id_factura}",
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{float(factura.total / 4000):.2f}",
                        },
                    }
                ],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "landing_page": "LOGIN",
                            "user_action": "PAY_NOW",
                            "return_url": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['paypal'])),
                            "cancel_url": request.build_absolute_uri(reverse('facturacion:retorno_pago', args=['paypal'])),
                        }
                    }
                },
            }
            resp = requests.post(f"{self.base_url}/v2/checkout/orders", json=payload, headers=headers, timeout=30)
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("id"):
                approve_link = next((link["href"] for link in data.get("links", []) if link["rel"] == "payer-action"), "")
                return PagoResultado(
                    exito=True,
                    transaction_id=data["id"],
                    mensaje="Orden PayPal creada",
                    redirect_url=approve_link,
                    raw_response=data,
                )
            return PagoResultado(exito=False, mensaje=f"Error PayPal: {data.get('message', 'desconocido')}")
        except ImportError:
            return PagoResultado(exito=False, mensaje="requests no instalado")
        except Exception as e:
            logger.exception("Error en PayPalGateway.crear_pago")
            return PagoResultado(exito=False, mensaje=str(e))

    def verificar_pago(self, transaction_id):
        try:
            import requests
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            resp = requests.get(f"{self.base_url}/v2/checkout/orders/{transaction_id}", headers=headers, timeout=30)
            data = resp.json()
            if resp.status_code == 200:
                estado = data.get("status")
                exito = estado == "COMPLETED"
                return PagoResultado(exito=exito, transaction_id=transaction_id, mensaje=f"PayPal {estado}", raw_response=data)
            return PagoResultado(exito=False, mensaje="No se pudo verificar")
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))

    def reembolsar(self, transaction_id, monto=None):
        try:
            import requests
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            url = f"{self.base_url}/v2/payments/captures/{transaction_id}/refund"
            payload = {"amount": {"value": f"{float(monto):.2f}", "currency_code": "USD"}} if monto else {}
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            exito = resp.status_code in (200, 201)
            return PagoResultado(exito=exito, transaction_id=transaction_id, mensaje="Reembolso OK" if exito else "Error")
        except Exception as e:
            return PagoResultado(exito=False, mensaje=str(e))


GATEWAY_MAP = {
    'mercadopago': MercadoPagoGateway,
    'wompi': WompiGateway,
    'paypal': PayPalGateway,
}


def get_gateway(codigo: str) -> IPaymentGateway:
    cls = GATEWAY_MAP.get(codigo)
    if not cls:
        raise ValueError(f"Gateway desconocido: {codigo}")
    return cls()
