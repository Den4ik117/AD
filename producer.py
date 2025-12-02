from __future__ import annotations

import json

import pika


def send_messages() -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672, virtual_host="local")
    )
    channel = connection.channel()
    channel.queue_declare(queue="product", durable=False)
    channel.queue_declare(queue="order", durable=False)

    products = [
        {
            "action": "create",
            "name": "Laptop Pro 14",
            "description": "14\" ноутбук для разработчиков",
            "price": 129900.0,
            "stock_quantity": 5,
        },
        {
            "action": "create",
            "name": "Mechanical Keyboard",
            "description": "Клавиатура с подсветкой",
            "price": 15990.0,
            "stock_quantity": 15,
        },
        {
            "action": "create",
            "name": "Wireless Mouse",
            "description": "Легкая беспроводная мышь",
            "price": 4990.0,
            "stock_quantity": 25,
        },
        {
            "action": "create",
            "name": "27\" Monitor",
            "description": "QHD IPS монитор",
            "price": 39990.0,
            "stock_quantity": 8,
        },
        {
            "action": "create",
            "name": "USB-C Hub",
            "description": "Хаб с Ethernet и HDMI",
            "price": 6990.0,
            "stock_quantity": 30,
        },
    ]

    for product in products:
        channel.basic_publish(
            exchange="",
            routing_key="product",
            body=json.dumps(product),
        )

    orders = [
        {
            "action": "create",
            "status": "pending",
            "user": {
                "username": "queue_buyer_1",
                "email": "queue_buyer_1@example.com",
                "description": "Покупатель техники",
            },
            "address": {
                "street": "Улица Тестовая, 1",
                "city": "Москва",
                "state": "Московская область",
                "zip_code": "101000",
                "country": "Россия",
                "is_primary": True,
            },
            "items": [
                {"product_name": "Laptop Pro 14", "quantity": 1},
                {"product_name": "Wireless Mouse", "quantity": 1},
            ],
        },
        {
            "action": "create",
            "status": "processing",
            "user": {
                "username": "queue_buyer_2",
                "email": "queue_buyer_2@example.com",
                "description": "Собирает сетап",
            },
            "address": {
                "street": "Проспект Победы, 42",
                "city": "Казань",
                "state": "Республика Татарстан",
                "zip_code": "420000",
                "country": "Россия",
                "is_primary": False,
            },
            "items": [
                {"product_name": "Mechanical Keyboard", "quantity": 1},
                {"product_name": "USB-C Hub", "quantity": 2},
            ],
        },
        {
            "action": "create",
            "status": "pending",
            "user": {
                "username": "queue_buyer_3",
                "email": "queue_buyer_3@example.com",
                "description": "Фанат больших мониторов",
            },
            "address": {
                "street": "Невский проспект, 12",
                "city": "Санкт-Петербург",
                "state": "Ленинградская область",
                "zip_code": "190000",
                "country": "Россия",
                "is_primary": True,
            },
            "items": [
                {"product_name": "27\" Monitor", "quantity": 1},
                {"product_name": "Wireless Mouse", "quantity": 2},
            ],
        },
    ]

    for order in orders:
        channel.basic_publish(
            exchange="",
            routing_key="order",
            body=json.dumps(order),
        )

    connection.close()


if __name__ == "__main__":
    send_messages()
