from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

project = "Crypto Telegram Bot"
author = "Anton, Maxim"
release = "1.0.1"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "ru"

html_theme = "alabaster"
html_title = "Crypto Telegram Bot"

autosummary_generate = True
autodoc_typehints = "description"
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
