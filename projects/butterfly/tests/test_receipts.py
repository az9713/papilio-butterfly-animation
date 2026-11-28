import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'development'))
import record_step


class ReceiptTests(unittest.TestCase):
    def test_a_downloaded_source_package_can_record_without_git(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(record_step,'ROOT',Path(folder)),patch.object(
                    record_step.subprocess,'run',side_effect=FileNotFoundError):
                path=record_step.save('test-step',{'accepted':True})
                self.assertIsNone(json.loads(path.read_text())['base_git_commit'])

    def test_a_recorded_event_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(record_step,'ROOT',Path(folder)),patch.object(
                    record_step.subprocess,'run',side_effect=FileNotFoundError):
                path=record_step.save('test-step',{'accepted':True});before=path.read_bytes()
                with self.assertRaises(FileExistsError):record_step.save('test-step',{'accepted':False})
                self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
