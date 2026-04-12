# scraper.py
import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9",
}


def get_snkrdunk_price(apparel_id: str) -> int | None:
    """
    スニダンの商品ページからJSON-LDのlowPrice（新品最安値）を取得する。
    URL: https://snkrdunk.com/apparels/{apparel_id}
    """
    if not apparel_id:
        return None
    url = f"https://snkrdunk.com/apparels/{apparel_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if data.get("@type") == "Product":
                    price = data.get("offers", {}).get("lowPrice")
                    if price is not None:
                        return int(price)
            except (json.JSONDecodeError, TypeError):
                continue
        return None
    except Exception:
        return None


def get_morimori_price(product_url: str) -> int | None:
    """
    森森買取の商品ページから現金買取価格（#price-target）を取得する。
    シュリンクなしは morimori_url=None で呼ばれないため考慮不要。
    """
    if not product_url:
        return None
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.find(id="price-target")
        if el:
            text = el.get_text(strip=True)   # 例: "14,600円"
            return int(re.sub(r"[^\d]", "", text))
        return None
    except Exception:
        return None


def fetch_prices(snkrdunk_id: str | None, morimori_url: str | None) -> dict:
    """
    1商品分の価格を両サイトから取得してdictで返す。
    {
        "snkrdunk": 16000 | None,
        "morimori": 14600 | None,
    }
    """
    return {
        "snkrdunk": get_snkrdunk_price(snkrdunk_id),
        "morimori": get_morimori_price(morimori_url),
    }
