import time
import googlemaps
from config import GOOGLE_PLACES_API_KEY

_client: googlemaps.Client | None = None


def _get_client() -> googlemaps.Client:
    global _client
    if _client is None:
        _client = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)
    return _client


def fetch_roofers(city: str, max_results: int = 60) -> list[dict]:
    client = _get_client()
    query = f"roofing contractor {city} UK"
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

    return {
        "place_id": place_id,
        "name": result.get("name", ""),
        "phone": _normalise_uk_phone(phone),
        "website": result.get("website", ""),
        "city": city,
        "review_count": result.get("user_ratings_total", 0),
        "rating": result.get("rating", 0.0),
    }


def _extract_city(components: list[dict]) -> str:
    for comp in components:
        if "postal_town" in comp.get("types", []):
            return comp["long_name"]
    for comp in components:
        if "locality" in comp.get("types", []):
            return comp["long_name"]
    return ""


def _normalise_uk_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit() or c == "+")
    if digits.startswith("0"):
        digits = "+44" + digits[1:]
    elif digits.startswith("44") and not digits.startswith("+"):
        digits = "+" + digits
    return digits
