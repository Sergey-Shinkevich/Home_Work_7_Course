import stripe
from django.conf import settings

# Инициализируем секретный ключ Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name):
    """Создает продукт в Stripe и возвращает его ID."""
    product = stripe.Product.create(name=name)
    return product.id


def create_stripe_price(amount, product_id):
    """
    Создает цену в Stripe для продукта.
    Сумма умножается на 100, так как Stripe принимает значения в копейках/центах.
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency="rub",
    )
    return price.id


def create_stripe_session(price_id):
    """
    Создает сессию оплаты в Stripe и возвращает ID сессии и ссылку на оплату.
    """
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url="http://127.0.0.1:8000/",
        cancel_url="http://127.0.0.1:8000/",
    )
    return session.id, session.url


def get_stripe_session_status(session_id):
    """
    Получает актуальные данные о сессии из Stripe по её ID.
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return {
        "status": session.status,  # например, 'complete', 'open', 'expired'
        "payment_status": session.payment_status,  # 'paid', 'unpaid'
        "amount_total": session.amount_total,
    }
