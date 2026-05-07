"""
One-time setup script
Run this first to create all directories and test client
"""

import os
from pathlib import Path
from client_database import ClientDatabase

def setup():
    print("🚀 Setting up RFP Intelligence Engine...\n")
    
    # Create directory structure
    directories = [
        "~/rfp-agent/data",
        "~/rfp-agent/data/client_files",
        "~/rfp-agent/templates",
        "~/rfp-agent/logs"
    ]
    
    for directory in directories:
        path = Path(os.path.expanduser(directory))
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {path}")
    
    # Initialize database
    db = ClientDatabase()
    
    # Add test client
    test_client = db.add_client(
        client_id="DEMO001",
        company_name="Demo Construction Co",
        email="demo@example.com",
        service_tier="full_stack",
        industry="construction"
    )
    
    print(f"\n✅ Created test client: {test_client['company_name']}")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Run: streamlit run demo_app.py")
    print("2. Upload a test RFP")
    print("3. See the magic happen!")

if __name__ == "__main__":
    setup()
