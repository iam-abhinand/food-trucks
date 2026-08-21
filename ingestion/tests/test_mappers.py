from ingestion.mappers import map_datasf_record
from trucks.models import FoodTruck


def _valid_record(**overrides):
    """Helper: returns a valid raw DataSF-shaped record, with optional field overrides."""
    base = {
        "objectid": "1343831",
        "applicant": "Got Snacks",
        "facilitytype": "Push Cart",
        "address": "1020 03RD ST",
        "permit": "19MFF-00112",
        "status": "REQUESTED",
        "fooditems": "sunflower seeds: crackerjacks",
        "latitude": "37.77551013804947",
        "longitude": "-122.39099930600248",
        "schedule": "http://bsm.sfdpw.org/example.pdf",
        "expirationdate": "2020-07-15T00:00:00.000",
    }
    base.update(overrides)
    return base


class TestMapDatasfRecord:
    def test_maps_valid_record_correctly(self):
        result = map_datasf_record(_valid_record())
        assert result["external_id"] == "1343831"
        assert result["applicant"] == "Got Snacks"
        assert result["status"] == FoodTruck.Status.REQUESTED
        assert result["latitude"] == 37.77551013804947
        assert result["longitude"] == -122.39099930600248

    def test_returns_none_when_objectid_missing(self):
        record = _valid_record()
        del record["objectid"]
        assert map_datasf_record(record) is None

    def test_returns_none_when_latitude_missing(self):
        record = _valid_record()
        del record["latitude"]
        assert map_datasf_record(record) is None

    def test_returns_none_when_coordinates_not_numeric(self):
        record = _valid_record(latitude="not-a-number")
        assert map_datasf_record(record) is None

    def test_unknown_status_maps_to_other(self):
        record = _valid_record(status="SOME_NEW_STATUS")
        result = map_datasf_record(record)
        assert result["status"] == FoodTruck.Status.OTHER

    def test_missing_applicant_defaults_to_unknown(self):
        record = _valid_record(applicant="")
        result = map_datasf_record(record)
        assert result["applicant"] == "Unknown"

    def test_missing_expiration_date_returns_none(self):
        record = _valid_record(expirationdate="")
        result = map_datasf_record(record)
        assert result["expiration_date"] is None

    def test_malformed_expiration_date_returns_none(self):
        record = _valid_record(expirationdate="not-a-date")
        result = map_datasf_record(record)
        assert result["expiration_date"] is None
