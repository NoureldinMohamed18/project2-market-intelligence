from src.storage import get_db


def avg_price_by_category(db):
    """متوسط السعر والتقييم وعدد الكتب لكل تصنيف."""
    pipeline = [
        {"$group": {
            "_id": "$category",
            "books": {"$sum": 1},
            "avg_price_gbp": {"$avg": "$price_gbp"},
            "avg_price_egp": {"$avg": "$price_egp"},
            "avg_rating": {"$avg": "$rating"},
        }},
        {"$sort": {"avg_price_gbp": -1}},
    ]
    return list(db.books.aggregate(pipeline))


def top_expensive(db, n=10):
    """أغلى n كتاب."""
    return list(
        db.books.find({}, {"_id": 0, "title": 1, "category": 1,
                           "price_gbp": 1, "price_egp": 1})
        .sort("price_gbp", -1)
        .limit(n)
    )


def best_value(db, n=10):
    """أرخص الكتب اللي تقييمها 5 ومتوفرة (أفضل قيمة مقابل السعر)."""
    pipeline = [
        {"$match": {"rating": 5, "in_stock": True}},   # الفلتر الأول دايماً
        {"$sort": {"price_gbp": 1}},
        {"$limit": n},
        {"$project": {"_id": 0, "title": 1, "category": 1,
                      "price_gbp": 1, "price_egp": 1}},
    ]
    return list(db.books.aggregate(pipeline))


def print_report():
    db = get_db()

    print("\n=== Average price by category (top 10 by GBP) ===")
    for row in avg_price_by_category(db)[:10]:
        egp = f"{row['avg_price_egp']:.0f}" if row["avg_price_egp"] else "n/a"
        print(f"{row['_id']:<22} books={row['books']:<4} "
              f"£{row['avg_price_gbp']:.2f}  EGP {egp:<6} "
              f"rating={row['avg_rating']:.2f}")

    print("\n=== 10 most expensive books ===")
    for b in top_expensive(db):
        print(f"£{b['price_gbp']:<6} {b['title'][:60]}  [{b['category']}]")

    print("\n=== Best value: 5-star, in stock, cheapest ===")
    for b in best_value(db):
        print(f"£{b['price_gbp']:<6} {b['title'][:60]}  [{b['category']}]")


if __name__ == "__main__":
    print_report()