from .es_client import es_client
from .indexes import INDEX_NAME


def search_trucks(query: str, size: int = 20) -> list[dict]:
    """
    Autocomplete-style search across applicant name and food items.
    Returns a list of raw ES hit dicts (each containing db_id, applicant,
    food_items, etc., plus the relevance score).
    """
    body = {
        "size": size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["applicant^2", "food_items"],
                # applicant^2 boosts matches in the truck name field to rank
                # twice as relevant as matches in food_items e.g. searching
                # "taco" should rank a truck literally named "Taco Truck"
                # above a truck that merely lists tacos among many food items.
                "type": "best_fields",
            }
        },
    }
    response = es_client.search(index=INDEX_NAME, body=body)
    hits = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        source["score"] = hit["_score"]
        hits.append(source)
    return hits
