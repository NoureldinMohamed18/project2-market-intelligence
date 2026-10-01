import logging
import os
from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient, UpdateOne

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "market_intel"


def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")          # لو السيرفر واقف نفشل هنا بوضوح
    return client[DB_NAME]


def save(clean, rejected):
    db = get_db()
    books = db["books"]
    books.create_index([("url", ASCENDING)], unique=True)
    books.create_index([("category", ASCENDING)])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if clean:
        ops = [
            UpdateOne(
                {"url": b["url"]},                       # دوّر على الكتاب بلينكه
                {"$set": b,                              # حدّث بياناته
                 "$setOnInsert": {"first_seen_at": now}},  # وقت أول ظهور (مرة واحدة بس)
                upsert=True,                             # لو مش موجود ضيفه
            )
            for b in clean
        ]
        result = books.bulk_write(ops, ordered=False)
        logger.info("Books: %d inserted | %d matched | %d total in collection",
                    result.upserted_count, result.matched_count,
                    books.count_documents({}))

    # المرفوض تقرير مراجعة، نستبدله كل مرة (زي المشروع الأول)
    db["books_rejected"].delete_many({})
    if rejected:
        db["books_rejected"].insert_many(rejected)
    logger.info("Rejected saved: %d", len(rejected))