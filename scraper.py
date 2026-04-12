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


def _fetch_snkrdunk_html(apparel_id: str) -> str | None:
    if not apparel_id:
        return None
    url = f"https://snkrdunk.com/apparels/{apparel_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def _parse_jsonld_product(html: str) -> dict | None:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # 配列で来るパターンもある
            if isinstance(data, list):
                for d in data:
                    if isinstance(d, dict) and d.get("@type") == "Product":
                        return d
            elif isinstance(data, dict) and data.get("@type") == "Product":
                return data
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def get_snkrdunk_price(apparel_id: str) -> int | None:
    """JSON-LDのlowPriceから新品最安値を取得"""
    html = _fetch_snkrdunk_html(apparel_id)
    data = _parse_jsonld_product(html)
    if not data:
        return None
    try:
        price = data.get("offers", {}).get("lowPrice")
        return int(price) if price is not None else None
    except (ValueError, TypeError):
        return None


def get_snkrdunk_image(apparel_id: str) -> str | None:
    """
    スニダンの商品ページから商品画像URLを取得する。
    優先順位: JSON-LD image → og:image → twitter:image
    """
    html = _fetch_snkrdunk_html(apparel_id)
    if not html:
        return None

    # 1. JSON-LD
    data = _parse_jsonld_product(html)
    if data:
        img = data.get("image")
        if isinstance(img, list) and img:
            return img[0]
        if isinstance(img, str) and img:
            return img

    # 2. og:image
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"]

    # 3. twitter:image
    tw = soup.find("meta", attrs={"name": "twitter:image"})
    if tw and tw.get("content"):
        return tw["content"]

    return None


def get_morimori_price(product_url: str) -> int | None:
    if not product_url:
        return None
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.find(id="price-target")
        if el:
            text = el.get_text(strip=True)
            return int(re.sub(r"[^\d]", "", text))
        return None
    except Exception:
        return None


def get_mobile_ichiban_price(product_url: str) -> int | None:
    if not product_url:
        return None
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
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
    snkr_price = get_snkrdunk_price(snkrdunk_id)
    mori_price = get_morimori_price(morimori_url)

    mobile_price = None
    if mori_price is None and mobile_ichiban_url:
        mobile_price = get_mobile_ichiban_price(mobile_ichiban_url)

    return {
        "snkrdunk": snkr_price,
        "morimori": mori_price,
        "mobile_ichiban": mobile_price,
    }
