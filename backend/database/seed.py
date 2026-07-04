import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.schema import init_database

if __name__ == "__main__":
    init_database()
