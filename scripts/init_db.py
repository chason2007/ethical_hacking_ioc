import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import engine, Base
from backend.models import Capture, Packet, Endpoint, Conversation, ProtocolStat, SecurityFinding

def init_database():
    print("[INFO] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Database tables created successfully.")

if __name__ == "__main__":
    init_database()
