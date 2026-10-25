"""Compatibility command for the single complete release; no separate web bundle."""
from build_release import main

if __name__ == '__main__':
    raise SystemExit(main())
