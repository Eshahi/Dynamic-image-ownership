"""Local reader rejection tests; never accesses real metadata or network."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from b3_diffusiondb_selection import SelectionError
from b3_read_diffusiondb_metadata import select_local_metadata


@unittest.skipUnless(importlib.util.find_spec("pyarrow"), "isolated metadata venv required")
class MetadataReaderTests(unittest.TestCase):
    def test_wrong_size_and_digest_fail_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metadata.parquet"
            path.write_bytes(b"notparquet")
            with self.assertRaisesRegex(SelectionError, "size mismatch"):
                select_local_metadata(path)
            with patch("b3_read_diffusiondb_metadata.EXPECTED_SIZE", 10):
                with self.assertRaisesRegex(SelectionError, "SHA-256 mismatch"):
                    select_local_metadata(path)


if __name__ == "__main__":
    unittest.main()
