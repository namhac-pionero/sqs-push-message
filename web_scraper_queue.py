import requests
from bs4 import BeautifulSoup
import logging
from sqs_sender import SQSMessageSender
from datetime import datetime
from dotenv import load_dotenv
import os
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


QUEUE_URL = os.getenv('QUEUE_URL')

WEB_SCRAPPER = os.getenv('WEB_SCRAPPER')
class WebScraperQueue:
    def __init__(self, queue_url, region_name='us-east-1'):
        """
        Initialize the web scraper with SQS configuration
        
        Args:
            queue_url (str): The URL of the SQS queue
            region_name (str): AWS region name (default: us-east-1)
        """
        self.sqs_sender = SQSMessageSender(queue_url, region_name)
        self.session = requests.Session()
        # Set a user agent to be more friendly to websites
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_crawl_list(self, url):
        """
        Scrape the crawl list elements from the webpage
        
        Args:
            url (str): The URL to scrape
        
        Returns:
            list: List of crawl items with their metadata
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find all elements matching the specific selector
            crawl_items = soup.select('#choose-crawl-list .collection-list-3.w-dyn-items .collection-item-5.w-dyn-item .heading-ultras')
            
            # Process each item individually
            processed_items = []
            for  _,item in enumerate(crawl_items, 1):
                item_data = {
                    'item_id': item.get_text(strip=True),
                    'content': item.get_text(strip=True),
                    'source_url': url,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status_code': response.status_code
                }
                processed_items.append(item_data)
            
            logger.info(f"Found {len(processed_items)} crawl items")
            return processed_items
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return None

    def queue_crawl_data(self, url):
        """
        Scrape crawl list data and send each item as a separate message to SQS
        
        Args:
            url (str): The URL to scrape
        
        Returns:
            tuple: (success_count, total_count)
        """
        items = self.scrape_crawl_list(url)
        total = self.calculate_average_volume(items)
        print(total)
        if not items:
            logger.error("No items found to queue")
            return (0, 0)

        success_count = 0
        total_count = len(items)

        for item in items:
            # Add message attributes for better tracking
            message_attributes = {
                'ContentType': {
                    'DataType': 'String',
                    'StringValue': 'crawl_item'
                },
                'Timestamp': {
                    'DataType': 'String',
                    'StringValue': item['timestamp']
                },
                'ItemId': {
                    'DataType': 'String',
                    'StringValue': str(item['item_id'])
                }
            }
            
            # Send individual message to SQS
            response = self.sqs_sender.send_message(item, message_attributes)
            
            if response:
                success_count += 1
                logger.info(f"Successfully queued item {item['item_id']}")
            else:
                logger.error(f"Failed to queue item {item['item_id']}")

        logger.info(f"Queued {success_count} out of {total_count} items from {url}")
        return (success_count, total_count)

    def calculate_average_volume(self, data):
        """
        Calculate the average volume of the data
        """
        average_volume = 0
        for _, item in enumerate(data, 1):
            response = self.session.get(f"https://data.commoncrawl.org/crawl-data/{item['item_id']}/index.html")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            volume = soup.select('table tbody tr')
            warcs = volume[1].select('td')
            if warcs:
                volume_value = warcs[-1].getText()
                average_volume += float(volume_value)
                print(average_volume)


        if len(data) > 0:
            average_volume 
        return average_volume

    
def main():
    # Example usage
    queue_url = QUEUE_URL  # Replace with your SQS queue URL
    scraper = WebScraperQueue(queue_url)
    
    # Scrape and queue crawl list data
    url = WEB_SCRAPPER # Replace with your target URL
    success_count, total_count = scraper.queue_crawl_data(url)
    
    print(f"Processing complete: {success_count} of {total_count} items successfully queued")

if __name__ == "__main__":
    main() 