# Frontend - React with Vite
import os
from pathlib import Path

frontend_dir = Path("frontend")
frontend_dir.mkdir(exist_ok=True)

# Create necessary subdirectories
(frontend_dir / "src" / "components").mkdir(parents=True, exist_ok=True)
(frontend_dir / "src" / "pages").mkdir(parents=True, exist_ok=True)
(frontend_dir / "src" / "services").mkdir(parents=True, exist_ok=True)

print("✓ Frontend directory structure created")
