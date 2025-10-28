from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import User, Address, Product, Order

connect_url = "sqlite:///test.db"
engine = create_engine(connect_url, echo=True)
session_factory = sessionmaker(engine)

def add_products_and_orders():
    
    with session_factory() as session:
        
        products = [
            Product(name="Молоко Простоквашино 2.5%", description="Пастеризованное молоко 1 л", price=89.90),
            Product(name="Хлеб Бородинский", description="Ржаной хлеб 500 гр", price=65.50),
            Product(name="Сыр Российский", description="Твердый сыр 200 гр", price=249.99),
            Product(name="Яйца куриные C1", description="Яйца столовые 10 шт", price=119.90),
            Product(name="Вода минеральная Боржоми", description="Лечебно-столовая вода 0,5 л", price=159.99)
        ]
        
        session.add_all(products)
        session.flush()  
        
        users = session.scalars(select(User)).all()
        addresses = session.scalars(select(Address)).all()
        
        orders = [
            Order(
                user_id=users[0].id,
                address_id=addresses[0].id,
                product_id=products[0].id,
                quantity=1,
                total_price=products[0].price,
                status="completed"
            ),
            Order(
                user_id=users[1].id,
                address_id=addresses[1].id,
                product_id=products[1].id,
                quantity=2,
                total_price=products[1].price * 2,
                status="pending"
            ),
            Order(
                user_id=users[2].id,
                address_id=addresses[2].id,
                product_id=products[2].id,
                quantity=1,
                total_price=products[2].price,
                status="completed"
            ),
            Order(
                user_id=users[3].id,
                address_id=addresses[3].id,
                product_id=products[3].id,
                quantity=3,
                total_price=products[3].price * 3,
                status="pending"
            ),
            Order(
                user_id=users[4].id,
                address_id=addresses[4].id,
                product_id=products[4].id,
                quantity=1,
                total_price=products[4].price,
                status="completed"
            )
        ]
        
        session.add_all(orders)
        session.commit()
        
        users = session.scalars(select(User)).all()
        user_descriptions = [
            "Постоянный клиент, любит молочные продукты",
            "Часто заказывает хлеб и выпечку", 
            "Предпочитает премиальные сыры",
            "Регулярно покупает яйца и воду",
            "Новый клиент, пробует разные товары"
        ]
        
        for i, user in enumerate(users):
            user.description = user_descriptions[i]
        
        session.commit()
        print("Продукты и заказы успешно добавлены")

if __name__ == "__main__":
    add_products_and_orders()

    