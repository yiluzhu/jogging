import os
import pytest

os.environ['IN_MEMORY_DB'] = 'Y'

args = [
    '--cov=../',
]

pytest.main(args)
