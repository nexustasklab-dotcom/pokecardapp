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


def get_mobile_ichiban_price(product_url: str) -> int | None:
    """
    モバイル一番の商品ページから買取価格を取得する。
    森森買取の代替として使用。
    """
    if not product_url:
        return None
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # label要素で最大価格を探す（text-rightクラス）
        price_labels = soup.find_all("label", class_="mb-0 text-right")
        if price_labels:
            prices = []
            for label in price_labels:
                text = label.get_text(strip=True)
                if "円" in text:
                    try:
                        price = int(re.sub(r"[^\d]", "", text))
                        if price > 0:
                            prices.append(price)
                    except ValueError:
                        continue
            return max(prices) if prices else None
        return None
    except Exception:
        return None


def fetch_prices(snkrdunk_id: str | None, morimori_url: str | None, mobile_ichiban_url: str | None = None) -> dict:
    """
    1商品分の価格を両サイトから取得してdictで返す。
    森森が取得できない場合はモバイル一番にフォールバック。
    {
        "snkrdunk": 16000 | None,
        "morimori": 14600 | None,
        "mobile_ichiban": 15000 | None (フォールバック時のみ),
    }
    """
    snkr_price = get_snkrdunk_price(snkrdunk_id)
    mori_price = get_morimori_price(morimori_url)
    
    # 森森が取得できず、モバイル一番URLがある場合はフォールバック
    mobile_price = None
    if mori_price is None and mobile_ichiban_url:
        mobile_price = get_mobile_ichiban_price(mobile_ichiban_url)
    
    return {
        "snkrdunk": snkr_price,
        "morimori": mori_price,
        "mobile_ichiban": mobile_price,
    }
