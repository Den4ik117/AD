from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Address, Order, OrderItem, Product, User

CONNECT_URL = "sqlite:///test.db"
engine = create_engine(CONNECT_URL, echo=True)
session_factory = sessionmaker(engine)


def add_products_and_orders():

    with session_factory() as session:

        products = [
            Product(
                name="Молоко Простоквашино 2.5%",
                description="Пастеризованное молоко 1 л",
                price=89.90,
                stock_quantity=120,
            ),
            Product(
                name="Хлеб Бородинский",
                description="Ржаной хлеб 500 гр",
                price=65.50,
                stock_quantity=60,
            ),
            Product(
                name="Сыр Российский",
                description="Твердый сыр 200 гр",
                price=249.99,
                stock_quantity=40,
            ),
            Product(
                name="Яйца куриные C1",
                description="Яйца столовые 10 шт",
                price=119.90,
                stock_quantity=200,
            ),
            Product(
                name="Вода минеральная Боржоми",
                description="Лечебно-столовая вода 0,5 л",
                price=159.99,
                stock_quantity=80,
            ),
        ]

        session.add_all(products)
        session.flush()

        users = session.scalars(select(User)).all()
        addresses = session.scalars(select(Address)).all()

        def build_order(
            user_idx: int,
            address_idx: int,
            product_payload: list[tuple[int, int]],
            status: str,
        ) -> Order:
            items = [
                OrderItem(
                    product_id=products[product_idx].id,
                    quantity=qty,
                    unit_price=products[product_idx].price,
                )
                for product_idx, qty in product_payload
            ]
            total_price = sum(item.quantity * item.unit_price for item in items)
            return Order(
                user_id=users[user_idx].id,
                address_id=addresses[address_idx].id,
                status=status,
                total_price=total_price,
                items=items,
            )

        orders = [
            build_order(0, 0, [(0, 1), (1, 2)], "completed"),
            build_order(1, 1, [(2, 1)], "pending"),
            build_order(2, 2, [(2, 1), (3, 3)], "completed"),
            build_order(3, 3, [(3, 2), (4, 1)], "pending"),
            build_order(4, 4, [(0, 1), (4, 2)], "completed"),
        ]

        session.add_all(orders)
        session.commit()

        users = session.scalars(select(User)).all()
        user_descriptions = [
            "Постоянный клиент, любит молочные продукты",
            "Часто заказывает хлеб и выпечку",
            "Предпочитает премиальные сыры",
            "Регулярно покупает яйца и воду",
            "Новый клиент, пробует разные товары",
        ]

        for i, user in enumerate(users):
            user.description = user_descriptions[i]

        session.commit()
        print("Продукты и заказы успешно добавлены")


if __name__ == "__main__":
    add_products_and_orders()
