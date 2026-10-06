import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.services.synthetic_pcap_generator import generate_demo_pcap

def main():
    out_file = ROOT_DIR / "sample-data" / "demo_capture.pcap"
    print(f"[INFO] Generating synthetic educational packet capture at {out_file}...")
    saved = generate_demo_pcap(out_file)
    print(f"[SUCCESS] Synthetic PCAP created ({saved.stat().st_size} bytes).")

if __name__ == "__main__":
    main()
