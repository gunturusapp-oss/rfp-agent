"""
Client Database Management
Handles multiple clients, their data, and service tiers
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ClientDatabase:
    def __init__(self, db_path="~/rfp-agent/data/clients.json"):
        self.db_path = os.path.expanduser(db_path)
        self.ensure_data_directory()
        self.clients = self.load_database()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        data_dir = os.path.dirname(self.db_path)
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        # Create client folders
        Path(os.path.expanduser("~/rfp-agent/data/client_files")).mkdir(parents=True, exist_ok=True)
    
    def load_database(self):
        """Load clients from JSON file"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_database(self):
        """Save clients to JSON file"""
        with open(self.db_path, 'w') as f:
            json.dump(self.clients, f, indent=2)
    
    def add_client(self, client_id, company_name, email, service_tier, industry):
        """
        Add new client to database
        
        service_tier: 'rfp_only', 'bundle', 'full_stack'
        """
        self.clients[client_id] = {
            'company_name': company_name,
            'email': email,
            'service_tier': service_tier,
            'industry': industry,
            'created_date': datetime.now().isoformat(),
            'rfps_processed': 0,
            'blogs_written': 0,
            'leads_generated': 0,
            'status': 'active',
            'past_wins': [],  # Store successful RFP examples
            'brand_voice': '',  # Their writing style
            'key_contacts': []  # Decision makers
        }
        
        # Create client folder
        client_folder = os.path.expanduser(f"~/rfp-agent/data/client_files/{client_id}")
        Path(client_folder).mkdir(parents=True, exist_ok=True)
        
        self.save_database()
        return self.clients[client_id]
    
    def get_client(self, client_id):
        """Retrieve client data"""
        return self.clients.get(client_id)
    
    def update_client(self, client_id, **kwargs):
        """Update client information"""
        if client_id in self.clients:
            self.clients[client_id].update(kwargs)
            self.save_database()
            return True
        return False
    
    def increment_service(self, client_id, service_type):
        """
        Track service usage
        service_type: 'rfp', 'blog', 'lead'
        """
        if client_id in self.clients:
            if service_type == 'rfp':
                self.clients[client_id]['rfps_processed'] += 1
            elif service_type == 'blog':
                self.clients[client_id]['blogs_written'] += 1
            elif service_type == 'lead':
                self.clients[client_id]['leads_generated'] += 1
            self.save_database()
    
    def get_all_active_clients(self):
        """Get list of all active clients"""
        return {k: v for k, v in self.clients.items() if v['status'] == 'active'}
    
    def get_clients_by_tier(self, tier):
        """Get clients by service tier"""
        return {k: v for k, v in self.clients.items() 
                if v['service_tier'] == tier and v['status'] == 'active'}


# Example usage
if __name__ == "__main__":
    db = ClientDatabase()
    
    # Add test client
    client = db.add_client(
        client_id="TEST001",
        company_name="Acme Construction",
        email="contact@acmeconstruction.com",
        service_tier="full_stack",
        industry="construction"
    )
    
    print(f"Added client: {client}")
    
    # Get client
    retrieved = db.get_client("TEST001")
    print(f"Retrieved: {retrieved}")
