import random
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.working_proxies: List[Dict[str, str]] = []
        self.last_refresh = 0
        self.refresh_interval = 1800  # 30 minutes

    def get_proxies(self) -> List[Dict[str, str]]:
        """Fetch free proxies from proxy list websites"""
        proxies = []
        
        # Try multiple sources for redundancy
        sources = [
            "https://www.sslproxies.org/",
            "https://free-proxy-list.net/"
        ]
        
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table', attrs={'class': 'table table-striped table-bordered'})
                    
                    if not table:
                        continue
                        
                    for row in table.find_all('tr')[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            ip = cells[0].text.strip()
                            port = cells[1].text.strip()
                            proxy = {
                                'http': f'http://{ip}:{port}',
                                'https': f'https://{ip}:{port}'
                            }
                            proxies.append(proxy)
                    
                    if proxies:
                        break  # If we got proxies from one source, we're good
            except Exception as e:
                logger.warning(f"Error fetching proxies from {source}: {e}")
        
        logger.info(f"Found {len(proxies)} potential proxies")
        return proxies

    def validate_proxy(self, proxy: Dict[str, str], timeout: int = 5) -> bool:
        """Test if a proxy works by connecting to Google"""
        try:
            test_url = "https://www.google.com"
            response = requests.get(
                test_url, 
                proxies=proxy, 
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy validation failed: {e}")
            return False

    def refresh_proxies(self) -> None:
        """Refresh the list of working proxies"""
        current_time = time.time()
        
        # Only refresh if it's been more than refresh_interval since last refresh
        if current_time - self.last_refresh < self.refresh_interval and self.working_proxies:
            return
        
        self.proxies = self.get_proxies()
        self.working_proxies = []
        
        for proxy in self.proxies:
            if self.validate_proxy(proxy):
                self.working_proxies.append(proxy)
                # Once we have at least 5 working proxies, we can stop validating
                if len(self.working_proxies) >= 5:
                    break
                
        logger.info(f"Refreshed proxies. Found {len(self.working_proxies)} working proxies")
        self.last_refresh = current_time

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random working proxy"""
        if not self.working_proxies or time.time() - self.last_refresh > self.refresh_interval:
            self.refresh_proxies()
            
        if not self.working_proxies:
            logger.warning("No working proxies available")
            return None
            
        return random.choice(self.working_proxies)

# Create a singleton instance
proxy_manager = ProxyManager()
