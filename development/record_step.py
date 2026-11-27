"""Execute a development step and retain a sanitized immutable evidence receipt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, str):
        for prefix in [str(ROOT),ROOT.as_posix(),json.dumps(str(ROOT))[1:-1]]:
            value=value.replace(prefix,'<project>')
        value = re.sub(r'(?i)[A-Z]:[/\\]+Users[/\\]+[^/\\\s"\']+', '<user-home>', value)
    return value


def save(event, data):
    folder = ROOT / 'development' / 'receipts'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (event + '.json')
    if path.exists():
        raise FileExistsError('Retain the prior receipt; use a new event ID: ' + event)
    sources=sorted(set(list(ROOT.glob('*.py'))+list((ROOT/'development').glob('*.py'))+
                       list((ROOT/'tests').glob('*.py'))+[ROOT/'config.json',ROOT/'wing-profiles.svg']))
    source_hashes={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in sources if path.is_file()}
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    payload = clean({'schema_version': 1, 'event': event,
                    'base_git_commit':git.stdout.strip() if git.returncode==0 else None,
                    'working_source_sha256':source_hashes,
                    'recorded_at_utc': datetime.now(timezone.utc).isoformat(), **data})
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return path


def run(event, command, *, expected_exit=0, cwd=ROOT, extra=None):
    result = subprocess.run([str(item) for item in command], cwd=cwd,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    accepted = result.returncode == expected_exit if expected_exit >= 0 else result.returncode != 0
    path = save(event, {'command': [str(item) for item in command], 'exit_code': result.returncode,
                        'expected_exit': expected_exit, 'accepted': accepted,
                        'stdout': result.stdout, 'stderr': result.stderr, **(extra or {})})
    print(json.dumps({'event': event, 'accepted': accepted,
                      'receipt': path.relative_to(ROOT).as_posix()}), flush=True)
    if not accepted:
        raise RuntimeError('Step failed; inspect ' + str(path))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('event')
    parser.add_argument('--expect', type=int, default=0)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('A command is required after --')
    run(args.event, command, expected_exit=args.expect)
