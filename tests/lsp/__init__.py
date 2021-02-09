import pathlib

import py

TEST_ROOT = py.path.local(__file__) / ".."
PROJECT_ROOT = TEST_ROOT / ".." / ".."
PROJECT_URI = pathlib.Path(PROJECT_ROOT).as_uri()
