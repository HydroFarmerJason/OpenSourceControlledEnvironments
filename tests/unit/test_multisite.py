from unittest.mock import patch

from src.multisite.manager import MultiSiteManager


def test_aggregate_data_success():
    manager = MultiSiteManager()
    site = manager.register_site("site1", {})
    with patch.object(site, "fetch_current_data", return_value={"temp": 20}):
        data = manager.aggregate_data()
    assert data == {"site1": {"temp": 20}}


def test_aggregate_data_connection_error():
    manager = MultiSiteManager()
    site = manager.register_site("site1", {})
    with patch.object(site, "fetch_current_data", side_effect=ConnectionError):
        data = manager.aggregate_data()
    assert data == {"site1": {"error": "connection"}}
