"""
Application for searching scientific articles on arXiv.
Allows searches by topic, author, or title/abstract with various sorting options.
"""

import json
import os
import time
from datetime import datetime
import arxiv


class UserInterface:
    """Manages user interaction: input, validation, and output."""
    
    def __init__(self):
        self.search_type = None
        self.search_query = None
        self.sort_by = None
        self.sort_order = None
        self.max_results = None
    
    def get_search_type(self):
        """Requests and validates the search type."""
        print("\n=== ARXIV ARTICLE SEARCH ===\n")
        print("Select the search type:")
        print("1 - By topic")
        print("2 - By author")
        print("3 - By title/abstract")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                self.search_type = choice
                return choice
            print("Invalid choice. Enter 1, 2, or 3.")
    
    def get_search_query(self):
        """Requests and validates the search text (max 100 characters)."""
        type_labels = {'1': 'topic', '2': 'author', '3': 'title/abstract'}
        label = type_labels.get(self.search_type, 'search')
        
        while True:
            query = input(f"\nEnter the text to search ({label}, max 100 characters): ").strip()
            if len(query) == 0:
                print("Text cannot be empty.")
            elif len(query) > 100:
                print(f"Text exceeds 100 characters (current: {len(query)}). Try again.")
            else:
                self.search_query = query
                return query
    
    def get_sort_by(self):
        """Requests and validates the sorting criterion."""
        print("\nSelect the sorting:")
        print("1 - Relevance")
        print("2 - Last updated")
        print("3 - Publication date")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                self.sort_by = choice
                return choice
            print("Invalid choice. Enter 1, 2, or 3.")
    
    def get_sort_order(self):
        """Requests and validates the sorting order."""
        print("\nSelect the order:")
        print("1 - Ascending")
        print("2 - Descending")
        
        while True:
            choice = input("\nEnter your choice (1-2): ").strip()
            if choice in ['1', '2']:
                self.sort_order = choice
                return choice
            print("Invalid choice. Enter 1 or 2.")
    
    def get_max_results(self):
        """Requests and validates the number of results (1-10)."""
        while True:
            num = input("\nEnter the number of desired results (1-10): ").strip()
            try:
                num_int = int(num)
                if 1 <= num_int <= 10:
                    self.max_results = num_int
                    return num_int
                else:
                    print("Number must be between 1 and 10.")
            except ValueError:
                print("Enter a valid number.")
    
    def collect_all_inputs(self):
        """Collects all inputs from the user."""
        self.get_search_type()
        self.get_search_query()
        self.get_sort_by()
        self.get_sort_order()
        self.get_max_results()
        
        return {
            'search_type': self.search_type,
            'search_query': self.search_query,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'max_results': self.max_results
        }
    
    def display_results_saved(self, file_path):
        """Displays the path of the saved file."""
        print(f"\nResults saved successfully!")
        print(f"File path: {file_path}")


class ArxivSearcher:
    """Manages queries to the arxiv library."""
    
    def __init__(self):
        # Configure client with more robust parameters
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,  # Pause between requests
            num_retries=5       # Number of retry attempts
        )
    
    def build_query(self, search_type, search_query):
        """Builds the query based on the search type."""
        # Mapping of search types to arXiv prefixes
        if search_type == '1':  # By topic
            return f"all:{search_query}"
        elif search_type == '2':  # By author
            return f"au:{search_query}"
        elif search_type == '3':  # By title/abstract
            return f"ti:{search_query} OR abs:{search_query}"
        return search_query
    
    def get_sort_criterion(self, sort_by):
        """Converts user choice to arxiv sorting criterion."""
        sort_mapping = {
            '1': arxiv.SortCriterion.Relevance,
            '2': arxiv.SortCriterion.LastUpdatedDate,
            '3': arxiv.SortCriterion.SubmittedDate
        }
        return sort_mapping.get(sort_by, arxiv.SortCriterion.Relevance)
    
    def get_sort_order(self, sort_order):
        """Converts user choice to arxiv sorting order."""
        order_mapping = {
            '1': arxiv.SortOrder.Ascending,
            '2': arxiv.SortOrder.Descending
        }
        return order_mapping.get(sort_order, arxiv.SortOrder.Descending)
    
    def search(self, search_params):
        """
        Performs the search on arXiv with automatic retry.
        
        Args:
            search_params: dictionary with search parameters
            
        Returns:
            list of results (arxiv.Result objects)
        """
        query = self.build_query(search_params['search_type'], search_params['search_query'])
        sort_by = self.get_sort_criterion(search_params['sort_by'])
        sort_order = self.get_sort_order(search_params['sort_order'])
        max_results = search_params['max_results']
        
        print(f"\nSearching on arXiv...")
        print(f"The arXiv server may take a few seconds...")
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Multiple attempts with exponential backoff
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                results = list(self.client.results(search))
                print(f"Found {len(results)} results")
                return results
                
            except arxiv.HTTPError as e:
                if attempt < max_attempts:
                    wait_time = 5 * attempt  # Exponential backoff: 5, 10, 15 seconds
                    print(f"ArXiv server temporarily unavailable (attempt {attempt}/{max_attempts})")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"\nHTTP error {e.status}: {e.entry.title}")
                    print("Suggestions:")
                    print("   - The arXiv server might be overloaded, try again in a few minutes")
                    print("   - Try reducing the number of results")
                    print("   - Check your internet connection")
                    raise
                    
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")
                raise


class ResultManager:
    """Manages JSON formatting and file saving."""
    
    def format_results(self, results):
        """
        Formats results into a JSON structure.
        
        Args:
            results: list of arxiv.Result objects
            
        Returns:
            list of dictionaries with formatted data
        """
        formatted_results = []
        
        for idx, result in enumerate(results, start=1):
            # Extract authors
            authors = [author.name for author in result.authors]
            
            # Extract publication date
            pub_date = result.published.strftime("%Y-%m-%d")
            
            # Extract journal name (if available)
            journal = result.journal_ref if result.journal_ref else "N/A"
            
            # Create short abstract (first 300 characters)
            abstract = result.summary.replace('\n', ' ').strip()
            if len(abstract) > 300:
                abstract = abstract[:297] + "..."
            
            formatted_result = {
                "id": idx,
                "authors": authors,
                "title": result.title,
                "publication_date": pub_date,
                "journal": journal,
                "link": result.entry_id,
                "abstract": abstract
            }
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def save_to_file(self, data, filename="articles.json"):
        """
        Saves results to a formatted JSON file.
        
        Args:
            data: list of dictionaries to save
            filename: file name (default: articles.json)
            
        Returns:
            absolute path of the saved file
        """
        # Get the absolute path of the file
        file_path = os.path.abspath(filename)
        
        # Save data in indented JSON format
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path


def main():
    """Main function that coordinates the program flow."""
    try:
        # 1. Collect input from user
        ui = UserInterface()
        search_params = ui.collect_all_inputs()
        
        # 2. Perform search on arXiv
        searcher = ArxivSearcher()
        results = searcher.search(search_params)
        
        if not results:
            print("\nNo results found for your search.")
            return
        
        # 3. Format and save results
        manager = ResultManager()
        formatted_data = manager.format_results(results)
        file_path = manager.save_to_file(formatted_data)
        
        # 4. Display file path to user
        ui.display_results_saved(file_path)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError during execution: {str(e)}")


if __name__ == "__main__":
    main()