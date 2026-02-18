"""
Batch Search Module - Search for multiple usernames simultaneously
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from tqdm import tqdm

from .core import CyberFind, SearchMode
from .models import SearchResult

logger = logging.getLogger("cyberfind")


class BatchSearch:
    """Batch search for multiple usernames with optimization"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    async def batch_search(
        self,
        usernames: List[str],
        sites_file: str = "quick.txt",
        mode: str = "standard",
    ) -> Dict[str, List[SearchResult]]:
        """
        Batch search for multiple usernames

        Args:
            usernames: List of usernames
            sites_file: File with site list
            mode: Search mode (standard, deep, stealth, aggressive)

        Returns:
            Dict with search results for each username
        """
        from .core import SearchMode

        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def search_with_limit(username: str):
            async with semaphore:
                try:
                    search_mode = SearchMode(mode)
                    found = await cf.search_async(
                        usernames=[username],
                        builtin_list=sites_file.replace(".txt", ""),
                        mode=search_mode,
                    )
                    return username, found.get("results", {}).get(username, {})
                except Exception as e:
                    logger.error(f"Batch search error for {username}: {e}")
                    return username, {}

        tasks = [search_with_limit(username) for username in usernames]

        progress_bar = tqdm(
            total=len(tasks),
            desc="Batch search",
            unit="user",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        for coro in asyncio.as_completed(tasks):
            username, found = await coro
            results[username] = found
            progress_bar.update(1)

        progress_bar.close()

        return results

    async def batch_search_by_site(
        self,
        usernames: List[str],
        site_name: str,
    ) -> Dict[str, bool]:
        """Quick search on a specific site for all usernames"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(username: str):
            async with semaphore:
                try:
                    # Load sites and find the specific one
                    sites = await cf.load_sites_async(builtin_list="all")
                    matching_site = next((s for s in sites if s.get("name") == site_name), None)

                    if matching_site:
                        result = await cf.check_site_async(
                            username, matching_site, SearchMode.STANDARD, asyncio.Semaphore(1)
                        )
                        return username, result.get("found", False)
                    return username, False
                except Exception as e:
                    logger.error(f"Error checking {site_name} for {username}: {e}")
                    return username, False

        tasks = [check_site(username) for username in usernames]

        progress_bar = tqdm(
            total=len(tasks),
            desc=f"Checking {site_name}",
            unit="user",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        for coro in asyncio.as_completed(tasks):
            username, exists = await coro
            results[username] = exists
            progress_bar.update(1)

        progress_bar.close()

        return results

    async def batch_search_multiple_sites(
        self,
        username: str,
        site_names: List[str],
    ) -> Dict[str, bool]:
        """Search for one username on multiple sites in parallel"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(site_name: str):
            async with semaphore:
                try:
                    # Load sites and find the specific one
                    sites = await cf.load_sites_async(builtin_list="all")
                    matching_site = next((s for s in sites if s.get("name") == site_name), None)

                    if matching_site:
                        result = await cf.check_site_async(
                            username, matching_site, SearchMode.STANDARD, asyncio.Semaphore(1)
                        )
                        return site_name, result.get("found", False)
                    return site_name, False
                except Exception as e:
                    logger.error(f"Error checking {site_name}: {e}")
                    return site_name, False

        tasks = [check_site(site) for site in site_names]

        progress_bar = tqdm(
            total=len(tasks),
            desc=f"Searching {username}",
            unit="site",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        for coro in asyncio.as_completed(tasks):
            site, exists = await coro
            results[site] = exists
            progress_bar.update(1)

        progress_bar.close()

        return results
