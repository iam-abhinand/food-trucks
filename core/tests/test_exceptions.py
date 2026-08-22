from unittest.mock import Mock, patch

from core.exceptions import custom_exception_handler


class TestCustomExceptionHandler:
    @patch("core.exceptions.drf_exception_handler")
    def test_returns_none_and_logs_when_drf_handler_returns_none(self, mock_drf_handler):
        # Simulates an unhandled exception (e.g. a genuine bug DRF doesn't
        # know how to turn into a response) — DRF's own handler returns None
        # in this case, and Django's default 500 handling takes over.
        mock_drf_handler.return_value = None
        mock_view = Mock()
        mock_view.__class__.__name__ = "SomeView"
        context = {"view": mock_view}
        result = custom_exception_handler(Exception("boom"), context)
        assert result is None

    @patch("core.exceptions.drf_exception_handler")
    def test_handles_missing_view_in_context_gracefully(self, mock_drf_handler):
        mock_drf_handler.return_value = None
        result = custom_exception_handler(Exception("boom"), {"view": None})
        assert result is None

    @patch("core.exceptions.drf_exception_handler")
    def test_wraps_dict_response_with_detail_key(self, mock_drf_handler):
        mock_response = Mock()
        mock_response.data = {"detail": "Not found."}
        mock_response.status_code = 404
        mock_drf_handler.return_value = mock_response
        result = custom_exception_handler(Exception(), {"view": None})
        assert result.data == {"error": {"message": "Not found.", "details": None}}

    @patch("core.exceptions.drf_exception_handler")
    def test_wraps_dict_response_without_detail_key_as_validation_error(self, mock_drf_handler):
        mock_response = Mock()
        mock_response.data = {"field_name": ["This field is required."]}
        mock_response.status_code = 400
        mock_drf_handler.return_value = mock_response
        result = custom_exception_handler(Exception(), {"view": None})
        assert result.data["error"]["message"] == "Validation failed."
        assert result.data["error"]["details"] == {"field_name": ["This field is required."]}

    @patch("core.exceptions.drf_exception_handler")
    def test_wraps_list_response_as_validation_error(self, mock_drf_handler):
        # Some DRF validation errors return a list at the top level
        # (e.g. non_field_errors on certain serializers).
        mock_response = Mock()
        mock_response.data = ["This field is required.", "Another error."]
        mock_response.status_code = 400
        mock_drf_handler.return_value = mock_response
        result = custom_exception_handler(Exception(), {"view": None})
        assert result.data["error"]["message"] == "Validation failed."
        assert result.data["error"]["details"] == [
            "This field is required.",
            "Another error.",
        ]
