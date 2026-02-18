"""
Custom Site Lists Module - Support for custom site lists

Supports standard URL templates with ``{username}`` substitution as well as
regex-based URL patterns prefixed with ``regex:``.  See :func:`cyber_find.utils.format_url`
for details on how regex patterns are resolved at query time.
"""

import os
from typing import Dict, List, Optional


class CustomSiteListManager:
    """Manages custom site lists"""

    def __init__(self, default_sites_dir: str = "sites"):
        """
        Initialize manager

        Args:
            default_sites_dir: Directory with built-in site lists
        """
        self.default_sites_dir = default_sites_dir
        self.custom_lists: Dict[str, List[Dict]] = {}
        self.default_lists: Dict[str, List[Dict]] = {}

    def load_site_list(self, file_path: str) -> List[Dict]:
        """
        Load site list from file

        Args:
            file_path: Path to file

        Returns:
            List of sites in format [{"name": "", "url": "", "category": "", "priority": ""}]
        """
        sites: List[Dict[str, str]] = []

        if not os.path.exists(file_path):
            return sites

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split("|")
                    if len(parts) >= 4:
                        site = {
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "category": parts[2].strip(),
                            "priority": parts[3].strip(),
                        }
                        sites.append(site)
        except Exception:
            pass

        return sites

    def load_custom_list(self, list_name: str, file_path: str) -> int:
        """
        Load custom site list

        Args:
            list_name: List name
            file_path: Path to file

        Returns:
            Number of loaded sites
        """
        sites = self.load_site_list(file_path)
        self.custom_lists[list_name] = sites
        return len(sites)

    def create_custom_list(
        self,
        list_name: str,
        sites: List[Dict],
        output_file: Optional[str] = None,
    ) -> int:
        """
        Create new custom list

        Args:
            list_name: List name
            sites: List of sites
            output_file: Optionally save to file

        Returns:
            Number of sites in list
        """
        self.custom_lists[list_name] = sites

        if output_file:
            self.save_list_to_file(output_file, sites)

        return len(sites)

    def save_list_to_file(self, file_path: str, sites: List[Dict]) -> None:
        """
        Save site list to file

        Args:
            file_path: Path to file
            sites: List of sites
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            for site in sites:
                line = f"{site['name']}|{site['url']}|{site.get('category', 'custom')}|{site.get('priority', '5')}\n"
                f.write(line)

    def merge_lists(
        self,
        list_names: List[str],
        remove_duplicates: bool = True,
    ) -> List[Dict]:
        """
        Merge multiple lists

        Args:
            list_names: List names to merge
            remove_duplicates: Remove duplicates by URL

        Returns:
            Merged list
        """
        merged = []
        seen_urls = set()

        for list_name in list_names:
            sites = self.custom_lists.get(list_name, [])
            for site in sites:
                url = site.get("url", "")

                if remove_duplicates:
                    if url not in seen_urls:
                        merged.append(site)
                        seen_urls.add(url)
                else:
                    merged.append(site)

        return merged

    def filter_by_category(
        self,
        list_name: str,
        category: str,
    ) -> List[Dict]:
        """
        Filter sites by category

        Args:
            list_name: List name
            category: Category

        Returns:
            Filtered list
        """
        sites = self.custom_lists.get(list_name, [])
        return [s for s in sites if s.get("category") == category]

    def filter_by_priority(
        self,
        list_name: str,
        min_priority: int = 1,
        max_priority: int = 10,
    ) -> List[Dict]:
        """
        Filter sites by priority

        Args:
            list_name: List name
            min_priority: Minimum priority
            max_priority: Maximum priority

        Returns:
            Filtered list
        """
        sites = self.custom_lists.get(list_name, [])

        def get_priority(site: Dict) -> int:
            try:
                return int(site.get("priority", 5))
            except ValueError:
                return 5

        return [s for s in sites if min_priority <= get_priority(s) <= max_priority]

    def add_site_to_list(
        self,
        list_name: str,
        site: Dict,
    ) -> None:
        """
        Add site to list

        Args:
            list_name: List name
            site: Site information
        """
        if list_name not in self.custom_lists:
            self.custom_lists[list_name] = []

        self.custom_lists[list_name].append(site)

    def remove_site_from_list(
        self,
        list_name: str,
        site_url: str,
    ) -> bool:
        """
        Remove site from list

        Args:
            list_name: List name
            site_url: Site URL

        Returns:
            True if site found and removed
        """
        if list_name not in self.custom_lists:
            return False

        sites = self.custom_lists[list_name]
        for i, site in enumerate(sites):
            if site.get("url") == site_url:
                sites.pop(i)
                return True

        return False

    def get_list_info(self, list_name: str) -> Dict:
        """
        Get list information

        Args:
            list_name: List name

        Returns:
            List information
        """
        sites = self.custom_lists.get(list_name, [])

        categories: Dict[str, int] = {}
        for site in sites:
            cat = site.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "name": list_name,
            "total_sites": len(sites),
            "categories": categories,
            "sites": sites,
        }

    def list_all_lists(self) -> List[str]:
        """
        Get names of all loaded lists

        Returns:
            List of names
        """
        return list(self.custom_lists.keys())

    def export_list_stats(self) -> Dict:
        """
        Export statistics for all lists

        Returns:
            Statistics for each list
        """
        stats = {}

        for list_name, sites in self.custom_lists.items():
            categories: Dict[str, int] = {}
            for site in sites:
                cat = site.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1

            stats[list_name] = {
                "total_sites": len(sites),
                "categories": categories,
            }

        return stats
