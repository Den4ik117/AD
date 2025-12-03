import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

try:
    r.ping()
    print("Успешное подключение к Redis")
except redis.ConnectionError:
    print("Ошибка подключения к Redis")

client = redis.Redis(host="localhost", port=6379, db=0)

client.set("user:name", "Иван")
name = client.get("user:name").decode("utf-8")

client.setex("session:123", 3600, "active")

client.set("counter", 0)
client.incr("counter")
client.incrby("counter", 5)
client.decr("counter")

client.lpush("tasks", "task1", "task2")
client.rpush("tasks", "task3", "task4")

tasks = client.lrange("tasks", 0, -1)
first_task = client.lpop("tasks")
last_task = client.rpop("tasks")
length = client.llen("tasks")

client.sadd("tags", "python", "redis", "database")
client.sadd("languages", "python", "java", "javascript")
is_member = client.sismember("tags", "python")
all_tags = client.smembers("tags")
intersection = client.sinter("tags", "languages")
union = client.sunion("tags", "languages")
difference = client.sdiff("tags", "languages")

client.hset(
    "user:1000",
    mapping={
        "name": "Иван",
        "age": "30",
        "city": "Москва",
    },
)

name = client.hget("user:1000", "name")
all_data = client.hgetall("user:1000")
exists = client.hexists("user:1000", "email")
keys = client.hkeys("user:1000")
values = client.hvals("user:1000")

client.zadd(
    "leaderboard",
    {
        "player1": 100,
        "player2": 200,
        "player3": 150,
    },
)

top_players = client.zrange("leaderboard", 0, 2, withscores=True)
players_by_score = client.zrangebyscore("leaderboard", 100, 200)
rank = client.zrank("leaderboard", "player1")
