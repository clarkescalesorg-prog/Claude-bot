import time
import googlemaps
from config import GOOGLE_PLACES_API_KEY
from leads.website_checker import score_website

_client: googlemaps.Client | None = None


def _get_client() -> googlemaps.Client:
    global _client
    if _client is None:
        _client = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)
    return _client


def fetch_roofers(city: str, max_results: int = 60) -> list[dict]:
    client = _get_client()
    query = f"roofing contractor {city} Florida"
    results = []
    response = client.places(query=query)

    while True:
        for place in response.get("results", []):
            details = _get_details(client, place["place_id"])
            if details:
                results.append(details)
            if len(results) >= max_results:
                return results
            time.sleep(0.1)  # stay under QPS limit

        next_token = response.get("next_page_token")
        if not next_token or len(results) >= max_results:
            break

        time.sleep(2)  # Google requires a short delay before using next_page_token
        response = client.places(query=query, page_token=next_token)

    return results


def _get_details(client: googlemaps.Client, place_id: str) -> dict | None:
    try:
        result = client.place(
            place_id,
            fields=["name", "formatted_phone_number", "website", "user_ratings_total", "rating", "address_components"],
        )["result"]
    except Exception:
        return None

    phone = result.get("formatted_phone_number", "")
    if not phone:
        return None  # skip leads with no phone number

    city = _extract_city(result.get("address_components", []))
    website = result.get("website", "")
    website_score = score_website(website)

    return {
        "place_id": place_id,
        "name": result.get("name", ""),
        "phone": _normalise_us_phone(phone),
        "website": website,
        "city": city,
        "review_count": result.get("user_ratings_total", 0),
        "rating": result.get("rating", 0.0),
        "website_score": website_score,
    }


def _extract_city(components: list[dict]) -> str:
    for comp in components:
        if "locality" in comp.get("types", []):
            return comp["long_name"]
    for comp in components:
        if "sublocality" in comp.get("types", []):
            return comp["long_name"]
    return ""


def _normalise_us_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return phone
