
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import get_latest_values
import logging

logging.basicConfig(level=logging.INFO)

def verify():
    print("Verifying get_latest_values()...")
    values = get_latest_values()
    
    print("\n--- Results ---")
    print(f"Latest Spot: {values['latest_spot']}")
    print(f"Prev Spot:   {values['prev_spot']}")
    print(f"Latest VIX:  {values['latest_vix']}")
    print(f"Prev VIX:    {values['prev_vix']}")
    
    # Basic validation
    if values['latest_vix'] > 0 and values['latest_vix'] != values['prev_vix']:
        print("\nSUCCESS: Latest VIX is valid and different from previous close (likely real-time).")
    else:
        print("\nWARNING: Latest VIX might be same as previous close or invalid.")

if __name__ == "__main__":
    verify()
