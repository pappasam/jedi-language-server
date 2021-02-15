import py
from .utils import as_uri

TEST_ROOT = py.path.local(__file__) / ".."
PROJECT_ROOT = TEST_ROOT / ".." / ".."
PROJECT_URI = as_uri(PROJECT_ROOT)
