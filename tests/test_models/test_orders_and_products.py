import pytest

from app.models import Address, Order, OrderItem, Product, User


def test_order_accepts_multiple_products(db_session):
    user = User(
        username="order_user",
        email="order@example.com",
        description="Любит заказывать много товаров",
    )
    db_session.add(user)
    db_session.flush()

    address = Address(
        user_id=user.id,
        street="Тестовая 1",
        city="Москва",
        state="Московская область",
        zip_code="101000",
        country="Россия",
        is_primary=True,
    )
    db_session.add(address)

    milk = Product(name="Молоко", description="1 л", price=89.9, stock_quantity=50)
    bread = Product(name="Хлеб", description="500 г", price=55.0, stock_quantity=35)
    db_session.add_all([milk, bread])
    db_session.flush()

    order = Order(
        user_id=user.id,
        address_id=address.id,
        status="pending",
        total_price=0,
    )
    order.items.extend(
        [
            OrderItem(product_id=milk.id, quantity=2, unit_price=milk.price),
            OrderItem(product_id=bread.id, quantity=1, unit_price=bread.price),
        ]
    )
    order.total_price = sum(item.quantity * item.unit_price for item in order.items)

    db_session.add(order)
    db_session.commit()

    stored_order = db_session.get(Order, order.id)
    assert stored_order is not None
    assert len(stored_order.items) == 2
    expected_total = 2 * milk.price + bread.price
    assert stored_order.total_price == pytest.approx(expected_total)
    product_ids = {item.product_id for item in stored_order.items}
    assert product_ids == {milk.id, bread.id}


def test_product_stock_quantity_persists_changes(db_session):
    product = Product(name="Сыр", description="200 г", price=249.99, stock_quantity=20)
    db_session.add(product)
    db_session.commit()

    created = db_session.get(Product, product.id)
    assert created is not None
    assert created.stock_quantity == 20

    created.stock_quantity -= 5
    db_session.commit()

    updated = db_session.get(Product, product.id)
    assert updated.stock_quantity == 15
