# scraper.py
import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
}


def _fetch_snkrdunk_html(apparel_id: str) -> str | None:
    url = f"https://snkrdunk.com/apparels/{apparel_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[snkrdunk] fetch error {apparel_id}: {e}")
        return None


def get_snkrdunk_info(apparel_id: str) -> dict | None:
    """
    スニダンから {name, price, image} を取得する。
    JSON-LD の Product のうち productID/sku が apparel_id と一致するものだけ採用。
    これによって同ページに混在する別商品(パック版等)を誤取得しない。
    """
    if not apparel_id:
        return None
    html = _fetch_snkrdunk_html(apparel_id)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    target = str(apparel_id)

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        for d in candidates:
            if not isinstance(d, dict) or d.get("@type") != "Product":
                continue
            pid = str(d.get("productID") or d.get("sku") or "")
            if pid != target:
                continue

            offers = d.get("offers") or {}
            price = offers.get("lowPrice") or offers.get("price")
            if price is None and isinstance(offers.get("offers"), list):
                # AggregateOffer の中の最初の offer から取る
                first = offers["offers"][0] if offers["offers"] else {}
                price = first.get("price")
            if price is None:
                continue

            img = d.get("image")
            if isinstance(img, list):
                img = img[0] if img else None

            try:
                return {
                    "name": d.get("name"),
                    "price": int(price),
                    "image": img,
                    "matched_id": apparel_id,
                }
            except (ValueError, TypeError):
                continue
    return None


def get_snkrdunk_price(apparel_id: str) -> int | None:
    info = get_snkrdunk_info(apparel_id)
    return info["price"] if info else None


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


def fetch_prices(snkrdunk_id: str | None, morimori_url: str | None,
                 mobile_ichiban_url: str | None = None) -> dict:
    info = get_snkrdunk_info(snkrdunk_id) if snkrdunk_id else None
    snkr_price = info["price"] if info else None
    snkr_name = info["name"] if info else None
    snkr_image = info["image"] if info else None

    mori_price = get_morimori_price(morimori_url)

    mobile_price = None
    if mori_price is None and mobile_ichiban_url:
        mobile_price = get_mobile_ichiban_price(mobile_ichiban_url)

    return {
        "snkrdunk": snkr_price,
        "snkrdunk_name": snkr_name,
        "snkrdunk_image": snkr_image,
        "morimori": mori_price,
        "mobile_ichiban": mobile_price,
    }


def fetch_prices_with_fallback(snkrdunk_id: str | None, morimori_url: str | None,
                               mobile_ichiban_url: str | None = None) -> dict:
    return fetch_prices(snkrdunk_id, morimori_url, mobile_ichiban_url)
