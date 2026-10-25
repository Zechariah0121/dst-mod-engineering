import sys
from pathlib import Path

# Resolve packaged modules explicitly, including isolated or deep-path launches.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dst_kb.cli import main
if __name__=='__main__':main()
