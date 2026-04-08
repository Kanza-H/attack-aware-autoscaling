"""
Smart scaler demo: uses the ML detector to decide whether to scale.
If detector says "attack" -> do NOT scale up. If "normal" -> allow scaling.
Run from project root: py scripts/scaler_demo.py [requests_per_sec] [errors]
Example: py scripts/scaler_demo.py 5 0     -> Normal, would scale if needed
         py scripts/scaler_demo.py 150 20   -> Attack, would NOT scale
"""
import sys
from pathlib import Path

# Add project root so we can import from ml
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.train_detector import predict

def main():
    if len(sys.argv) >= 3:
        rps = int(sys.argv[1])
        errs = int(sys.argv[2])
    else:
        rps = 5
        errs = 0
        print("Using default: requests_per_sec=5, errors=0 (use: py scripts/scaler_demo.py <rps> <errors>)")

    label = predict(rps, errs)
    print(f"Current: requests_per_sec={rps}, errors={errs}")
    print(f"Detector says: {label!r}")

    if label == "attack":
        print("Scaler decision: ATTACK DETECTED -> do NOT add servers; block attack traffic (save cost, defend)")
    else:
        print("Scaler decision: Normal traffic -> add new servers when servers get full (scale up)")

if __name__ == "__main__":
    main()
