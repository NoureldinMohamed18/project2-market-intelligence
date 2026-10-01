import json
import logging
from datetime import date
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

API_URL = "https://open.er-api.com/v6/latest/GBP"
CACHE_FILE = Path("data/cache/fx_gbp_egp.json")


def get_gbp_to_egp(timeout=10):
    """يرجّع سعر الجنيه الإسترليني بالجنيه المصري، أو None لو مقدرش."""
    today = date.today().isoformat()

    # 1) لو جبناه النهاردة، نستخدمه من الملف
    if CACHE_FILE.exists():
        cached = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if cached.get("date") == today:
            return cached["rate"]

    # 2) نطلبه من الـ API
    try:
        resp = requests.get(API_URL, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") != "success":
            raise ValueError(f"API returned: {data.get('result')}")
        rate = float(data["rates"]["EGP"])
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error("Could not fetch exchange rate: %s", e)
        return None

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"date": today, "rate": rate}), encoding="utf-8")
    logger.info("Fetched GBP->EGP rate: %.4f", rate)
    return rate