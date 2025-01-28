import importlib
import logging
import os
import sys


class ScraperLoader:
    @staticmethod
    def load_scraper(source: str):
        """
        Dynamically imports the scraper class based on the source.

        Args:
            source (str): The source name.  

        Returns:
            type: The dynamically imported Scraper class.

        Raises:
            ImportError: If the scraper cannot be found.
        """
        module_paths = [
            f"app.scrapers.{source.lower()}.scraper", # First attempt: <source>.common
            # f"app.scrapers.{source.lower()}.common", # Fallback: <source>.src.scraper
        ]

        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)
                logging.info(f"Successfully imported module: {module_path}")
                if hasattr(module, "Scraper"):
                    return module.Scraper
                else:
                    raise ImportError(f"Module '{module_path}' does not contain a Scraper class.")
            except ModuleNotFoundError as e:
                logging.warning(f"Module not found: {module_path}. Error: {e}")
                continue

        raise ImportError(f"Scraper for source '{source}' could not be loaded.")

    @staticmethod
    def initialize_scraper(source: str, **kwargs):
        """
        Instantiates the dynamically imported Scraper class.

        Args:
            source (str): The source name.
            **kwargs: Additional keyword arguments for the Scraper constructor.

        Returns:
            Scraper: An instance of the imported Scraper class.
        """
        scraper_class = ScraperLoader.load_scraper(source)
        return scraper_class(**kwargs)


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        source = "rapido"

        # Dynamically load and instantiate the scraper
        scraper_instance = ScraperLoader.initialize_scraper(source)

        # Assuming the scraper class has a scrape method
        print(f"Successfully loaded scraper: {scraper_instance.__class__.__name__}")
    except ImportError as e:
        logging.error(f"Failed to load scraper: {e}")
