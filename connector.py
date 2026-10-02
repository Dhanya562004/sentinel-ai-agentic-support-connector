"""
SentinelAI - Connector Layer (Simulated APIs)
Provides data access to customer support tickets with case-insensitive search and robust error handling.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "tickets.json")

class TicketConnector:
    """Simulated API Connector for Customer Support Data Access."""
    
    def __init__(self, data_file: str = DATA_PATH):
        self.data_file = data_file
        self._tickets: List[Dict[str, Any]] = self._load_tickets()

    def _load_tickets(self) -> List[Dict[str, Any]]:
        """Safely load tickets from JSON file with error handling."""
        if not os.path.exists(self.data_file):
            print(f"[Connector Warning] Data file not found at {self.data_file}. Returning empty dataset.")
            return []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Connector Error] Failed to parse {self.data_file}: {e}")
            return []

    def reload(self):
        """Reload tickets dataset from disk."""
        self._tickets = self._load_tickets()

    def list_tickets(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tickets, optionally filtered by status and/or priority.
        Case-insensitive filter matching.
        """
        results = self._tickets
        if status:
            results = [t for t in results if t.get("status", "").lower() == status.lower()]
        if priority:
            results = [t for t in results if t.get("priority", "").lower() == priority.lower()]
        return results

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single ticket by ID (case-insensitive).
        Returns None if not found or input is invalid.
        """
        if not ticket_id or not isinstance(ticket_id, str):
            return None
        
        clean_id = ticket_id.strip().lower()
        for ticket in self._tickets:
            if ticket.get("id", "").lower() == clean_id:
                return ticket
        return None

    def search_tickets(self, query: str) -> List[Dict[str, Any]]:
        """
        Case-insensitive search across ticket ID, title, description, category, and customer_name.
        Returns matching tickets sorted by relevance score.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return []

        clean_query = query.strip().lower()
        terms = re.findall(r'\w+', clean_query)
        
        matches_with_score = []

        for ticket in self._tickets:
            tid = ticket.get("id", "").lower()
            title = ticket.get("title", "").lower()
            desc = ticket.get("description", "").lower()
            category = ticket.get("category", "").lower()
            customer = ticket.get("customer_name", "").lower()

            score = 0
            
            # Exact match bonus
            if clean_query == tid:
                score += 100
            if clean_query in title:
                score += 30
            if clean_query in desc:
                score += 15
            if clean_query in category:
                score += 20
            if clean_query in customer:
                score += 25

            # Term overlap score
            for term in terms:
                if len(term) < 2:
                    continue
                if term in tid:
                    score += 10
                if term in title:
                    score += 5
                if term in desc:
                    score += 2
                if term in category:
                    score += 4
                if term in customer:
                    score += 4

            if score > 0:
                matches_with_score.append((score, ticket))

        # Sort by relevance score descending
        matches_with_score.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matches_with_score]


# Module level test & quick execution check
if __name__ == "__main__":
    connector = TicketConnector()
    print(f"Loaded {len(connector.list_tickets())} tickets.")
    search_res = connector.search_tickets("payment failed")
    print(f"Search 'payment failed' found {len(search_res)} tickets.")
    if search_res:
        print("Top match:", search_res[0]["id"], "-", search_res[0]["title"])
