from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "Package/src"))
sys.path.insert(0, str(root / "Instructor Guide/Reference"))
