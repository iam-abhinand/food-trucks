from core.geo import bounding_box, haversine_distance_km


class TestHaversineDistanceKm:
    def test_distance_between_identical_points_is_zero(self):
        distance = haversine_distance_km(37.7749, -122.4194, 37.7749, -122.4194)
        assert distance == 0

    def test_distance_between_sf_landmarks(self):
        # Ferry Building to Golden Gate Bridge, SF — real-world distance is
        # approximately 7.7 km, verified via Google Maps straight-line distance.
        ferry_building = (37.7955, -122.3937)
        golden_gate_bridge = (37.8199, -122.4783)
        distance = haversine_distance_km(*ferry_building, *golden_gate_bridge)
        assert 7.0 < distance < 8.5

    def test_distance_is_symmetric(self):
        point_a = (37.7749, -122.4194)
        point_b = (37.8044, -122.2712)
        distance_ab = haversine_distance_km(*point_a, *point_b)
        distance_ba = haversine_distance_km(*point_b, *point_a)
        assert round(distance_ab, 6) == round(distance_ba, 6)


class TestBoundingBox:
    def test_returns_box_centered_around_point(self):
        box = bounding_box(lat=37.7749, lon=-122.4194, radius_km=5)
        assert box["min_lat"] < 37.7749 < box["max_lat"]
        assert box["min_lon"] < -122.4194 < box["max_lon"]

    def test_larger_radius_produces_larger_box(self):
        small_box = bounding_box(lat=37.7749, lon=-122.4194, radius_km=1)
        large_box = bounding_box(lat=37.7749, lon=-122.4194, radius_km=10)
        small_lat_span = small_box["max_lat"] - small_box["min_lat"]
        large_lat_span = large_box["max_lat"] - large_box["min_lat"]
        assert large_lat_span > small_lat_span
