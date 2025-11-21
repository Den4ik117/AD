from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Address, Order, OrderItem, Product, User

engine = create_engine("sqlite:///test.db", echo=True)
session_factory = sessionmaker(engine)


def simple_join_query():

    with session_factory() as session:

        stmt = (
            select(
                User.username,
                User.description,
                Product.name,
                OrderItem.quantity,
                OrderItem.unit_price,
                Order.total_price,
                Order.status,
                Address.street,
                Address.city,
            )
            .select_from(Order)
            .join(Order.user)
            .join(Order.address)
            .join(Order.items)
            .join(OrderItem.product)
            .order_by(User.username)
        )

        results = session.execute(stmt).all()

        for row in results:
            print(f"{row.username}")
            print(f"{row.description}")
            print(f"{row.name} x{row.quantity} @ {row.unit_price}")
            print(f"{row.status} total: {row.total_price}")
            print(f"{row.street}, {row.city}")


if __name__ == "__main__":
    simple_join_query()
