"""Simple multi-site management utilities."""
from __future__ import annotations

from typing import Dict, Any


class RemoteSite:
    def __init__(self, site_id: str, connection_params: dict) -> None:
        self.site_id = site_id
        self.connection_params = connection_params

    def fetch_current_data(self) -> Dict[str, Any]:
        """Fetch current data from the remote site."""
        # Placeholder implementation
        return {"status": "ok"}


class CentralDashboard:
    def __init__(self) -> None:
        self.sites: Dict[str, RemoteSite] = {}

    def add_site(self, site: RemoteSite) -> None:
        self.sites[site.site_id] = site


class MultiSiteManager:
    def __init__(self) -> None:
        self.sites: Dict[str, RemoteSite] = {}
        self.central_dashboard = CentralDashboard()

    def register_site(self, site_id: str, connection_params: dict) -> RemoteSite:
        site = RemoteSite(site_id, connection_params)
        self.sites[site_id] = site
        self.central_dashboard.add_site(site)
        return site

    def aggregate_data(self) -> Dict[str, Any]:
        aggregated: Dict[str, Any] = {}
        for site_id, site in self.sites.items():
            try:
                data = site.fetch_current_data()
                aggregated[site_id] = data
            except ConnectionError:
                aggregated[site_id] = {"error": "connection"}
        return aggregated
