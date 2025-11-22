#!/usr/bin/env python3
"""
AegisMatrix Training Runner - Train all ML engines

Common script to train all three engines in sequence:
1. Direction Engine (BiLSTM + XGBoost) - 45 seconds
2. Seller Engine (3× XGBoost) - 10 seconds
3. Buyer Engine (3× XGBoost) - 5 seconds

Total time: ~60 seconds on CPU

Usage:
    python train_all.py              # Train all engines
    python train_all.py --engine direction  # Train only direction
    python train_all.py --engine seller     # Train only seller
    python train_all.py --engine buyer      # Train only buyer

Models output to: models/
"""

import sys
import time
import subprocess
import logging
from pathlib import Path
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent


def run_training_script(script_name, description):
    """Run a training script and handle errors."""
    script_path = PROJECT_ROOT / script_name
    
    logger.info("=" * 70)
    logger.info(f"Starting {description}...")
    logger.info(f"Script: {script_path}")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            timeout=300  # 5 minute timeout per script
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✓ {description} completed successfully in {elapsed:.1f}s")
            return True
        else:
            logger.error(f"✗ {description} failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} timed out (>5 minutes)")
        return False
    except Exception as e:
        logger.error(f"✗ {description} encountered error: {e}")
        return False


def train_all():
    """Train all three engines."""
    logger.info("Starting AegisMatrix ML Training Pipeline")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    start_time = time.time()
    results = {}
    
    # Train Direction Engine
    results['direction'] = run_training_script(
        'direction/train_direction.py',
        'Direction Engine (AegisCore)'
    )
    
    if not results['direction']:
        logger.warning("Direction training failed, continuing with other engines...")
    
    # Train Seller Engine
    results['seller'] = run_training_script(
        'seller/train_seller.py',
        'Seller Engine (RangeShield)'
    )
    
    if not results['seller']:
        logger.warning("Seller training failed, continuing with buyer engine...")
    
    # Train Buyer Engine
    results['buyer'] = run_training_script(
        'buyer/train_buyer.py',
        'Buyer Engine (TrendScout)'
    )
    
    # Summary
    total_time = time.time() - start_time
    
    logger.info("=" * 70)
    logger.info("TRAINING SUMMARY")
    logger.info("=" * 70)
    
    for engine, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{engine.upper():12} {status}")
    
    all_success = all(results.values())
    logger.info("=" * 70)
    logger.info(f"Total time: {total_time:.1f}s")
    
    if all_success:
        logger.info("✓ All engines trained successfully!")
        logger.info("Models ready for inference at: models/")
        return 0
    else:
        logger.warning("⚠ Some engines failed - check logs above")
        return 1


def train_single_engine(engine_name):
    """Train a single engine."""
    engine_map = {
        'direction': ('direction/train_direction.py', 'Direction Engine (AegisCore)'),
        'seller': ('seller/train_seller.py', 'Seller Engine (RangeShield)'),
        'buyer': ('buyer/train_buyer.py', 'Buyer Engine (TrendScout)'),
    }
    
    if engine_name not in engine_map:
        logger.error(f"Unknown engine: {engine_name}")
        logger.error(f"Available engines: {', '.join(engine_map.keys())}")
        return 1
    
    script, description = engine_map[engine_name]
    success = run_training_script(script, description)
    
    return 0 if success else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AegisMatrix Training Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_all.py                        # Train all engines
  python train_all.py --engine direction     # Train only direction
  python train_all.py --engine seller        # Train only seller
  python train_all.py --engine buyer         # Train only buyer
        """
    )
    
    parser.add_argument(
        '--engine',
        choices=['direction', 'seller', 'buyer'],
        help='Train specific engine only'
    )
    
    args = parser.parse_args()
    
    if args.engine:
        return train_single_engine(args.engine)
    else:
        return train_all()


if __name__ == '__main__':
    sys.exit(main())
