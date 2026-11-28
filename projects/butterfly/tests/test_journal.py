"""Regression checks for the actual standalone journal handoff failures."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'development'))
import update_journey


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'development/receipts').mkdir(parents=True)
        for name in ['index.html','config.json','development/history.json','development/environment-tested.json']:
            (self.root/name).write_bytes((ROOT/name).read_bytes())
        self.previous=json.loads((self.root/'development/history.json').read_text())
        self.previous['historical_stages'].append({'stage':'Later retained decision','decision':'Keep me',
                                                  'origin':'test fixture','evidence':[]})
        (self.root/'development/history.json').write_text(json.dumps(self.previous))
        (self.root/'development/receipts/new-event.json').write_text('{"event":"new-event","accepted":true}')
        (self.root/'development/receipts/index.json').write_text('[]')
        self.patch=patch.object(update_journey,'ROOT',self.root)
        self.patch.start();self.addCleanup(self.patch.stop)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_missing_media_and_git_use_labelled_history_and_preserve_receipts(self):
        before=self.snapshot()
        with patch.object(update_journey.subprocess,'check_output',side_effect=AssertionError('No tools needed')):
            update_journey.main()
            update_journey.main()  # A second refresh must retain the same historical identity.
        history=json.loads((self.root/'development/history.json').read_text())
        self.assertEqual(history['git_history'],self.previous['git_history'])
        self.assertIn('retained',history['git_history_origin']['mode'])
        self.assertEqual(history['historical_stages'][-1],self.previous['historical_stages'][-1])
        old={e['path']:e['sha256'] for s in self.previous['historical_stages'] for e in s['evidence']}
        for stage in history['historical_stages']:
            for entry in stage['evidence']:
                self.assertEqual(entry['sha256'],old[entry['path']])
                self.assertIn('retained',entry['hash_origin'])
        self.assertEqual((self.root/'development/environment-tested.json').read_bytes(),before['development/environment-tested.json'])
        self.assertEqual((self.root/'development/receipts/new-event.json').read_bytes(),before['development/receipts/new-event.json'])
        inventory=json.loads((self.root/'development/receipts/index.json').read_text())
        self.assertEqual(inventory[0]['event'],'new-event')
        self.assertIn(update_journey.BASE+'papilio-final-1080p.mp4',(self.root/'development/index.html').read_text())

    def test_present_evidence_is_measured_not_claimed_from_history(self):
        (self.root/'concept-v01.png').write_bytes(b'new local edit')
        update_journey.main()
        entry=json.loads((self.root/'development/history.json').read_text())['historical_stages'][0]['evidence'][0]
        self.assertEqual(entry['sha256'],update_journey.sha256(self.root/'concept-v01.png'))
        self.assertEqual(entry['hash_origin'],'measured from present file')

    def test_git_binary_absent_uses_snapshot(self):
        (self.root/'.git').mkdir()
        with patch.object(update_journey.subprocess,'check_output',side_effect=FileNotFoundError):
            update_journey.main()
        self.assertIn('retained',json.loads((self.root/'development/history.json').read_text())['git_history_origin']['mode'])

    def test_missing_digest_fails_before_any_outputs_change(self):
        previous=copy.deepcopy(self.previous)
        previous['historical_stages'][0]['evidence'][0]['sha256']='invalid'
        (self.root/'development/history.json').write_text(json.dumps(previous))
        before=self.snapshot()
        with self.assertRaisesRegex(FileNotFoundError,'retained digest'):update_journey.main()
        self.assertEqual(self.snapshot(),before)

    def test_invalid_receipt_fails_before_any_outputs_change(self):
        (self.root/'development/receipts/broken.json').write_text('not json')
        before=self.snapshot()
        with self.assertRaises(json.JSONDecodeError):update_journey.main()
        self.assertEqual(self.snapshot(),before)

    def test_invalid_git_snapshot_fails_before_any_outputs_change(self):
        self.previous['git_history']=[]
        (self.root/'development/history.json').write_text(json.dumps(self.previous))
        before=self.snapshot()
        with self.assertRaisesRegex(ValueError,'Git-history snapshot'):update_journey.main()
        self.assertEqual(self.snapshot(),before)


if __name__=='__main__':unittest.main()
