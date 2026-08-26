import datetime
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hooks import post_gen_project


class PostGenerationHookTest(unittest.TestCase):
    def test_replaces_generation_date_placeholder_in_documentation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            docs_dir.mkdir()
            log_path = docs_dir / "ENGINEERING_LOGS.md"
            log_path.write_text("Generated at {GENERATION_DATE}\n")

            fixed_now = datetime.datetime(
                2026,
                6,
                27,
                12,
                34,
                56,
                tzinfo=datetime.timezone.utc,
            )

            with (
                mock.patch.object(post_gen_project, "Path", side_effect=lambda path: Path(tmpdir) / path),
                mock.patch.object(post_gen_project.datetime, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = fixed_now
                post_gen_project.replace_generation_date_placeholders()

            self.assertEqual(
                log_path.read_text(),
                f"Generated at {fixed_now.astimezone().isoformat(timespec='seconds')}\n",
            )


if __name__ == "__main__":
    unittest.main()
