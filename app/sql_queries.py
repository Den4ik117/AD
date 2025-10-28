from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import User, Address, Product, Order

engine = create_engine("sqlite:///test.db", echo=True)
session_factory = sessionmaker(engine)

def simple_join_query():
    
    with session_factory() as session:
        
        stmt = select(
            User.username,
            User.description,
            Product.name,
            Order.quantity,
            Order.total_price,
            Order.status,
            Address.street,
            Address.city
        ).select_from(Order).join(
            Order.user
        ).join(
            Order.product  
        ).join(
            Order.address
        ).order_by(
            User.username
        )
        
        results = session.execute(stmt).all()
        
        for row in results:
            print(f"{row.username}")
            print(f"{row.description}")
            print(f"{row.name} x{row.quantity}")
            print(f"{row.status}")
            print(f"{row.street}, {row.city}")
           

if __name__ == "__main__":
    simple_join_query()