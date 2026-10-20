#!/usr/bin/env python3
"""Repository consistency gate for the locked CourseLock release surface."""
import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit('source consistency failed: ' + message)


def main() -> None:
    primary = ROOT / 'contracts' / 'courselock.py'
    consumer = ROOT / 'contracts' / 'course_consumer.py'
    if not primary.is_file() or not consumer.is_file():
        fail('both contract sources are required')
    primary_source = primary.read_text(encoding='utf-8')
    consumer_source = consumer.read_text(encoding='utf-8')
    ast.parse(primary_source)
    ast.parse(consumer_source)
    primary_header = primary_source.splitlines()[0]
    if primary_header != consumer_source.splitlines()[0]:
        fail('contract GenVM runner headers differ')
    package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
    if package.get('devDependencies', {}).get('genlayer') != '0.39.1':
        fail('package.json is not pinned to genlayer 0.39.1')
    lock_path = ROOT / 'package-lock.json'
    if not lock_path.is_file():
        fail('package-lock.json is required')
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    locked_genlayer = lock.get('packages', {}).get('node_modules/genlayer', {}).get('version')
    if locked_genlayer != '0.39.1':
        fail('package-lock.json is not consistent with genlayer 0.39.1')
    requirements = (ROOT / 'requirements-dev.txt').read_text(encoding='utf-8')
    for required in ('genlayer-test==0.29.0', 'genvm-linter==0.11.0'):
        if required not in requirements:
            fail('missing exact Python pin: ' + required)
    config = (ROOT / 'gltest.config.yaml').read_text(encoding='utf-8')
    if 'https://studio.genlayer.com/api' not in config or 'default: studionet' not in config:
        fail('gltest configuration is not stable StudioNet')
    guard = (ROOT / 'scripts' / 'assert_studionet.mjs').read_text(encoding='utf-8')
    if 'STABLE_CHAIN=61999' not in guard or 'STABLE_RPC=\'https://studio.genlayer.com/api\'' not in guard:
        fail('network guard is not pinned to stable StudioNet 61999')
    if '61997' in primary_source + consumer_source + config + guard:
        fail('preview chain 61997 appears in the release surface')
    forbidden = {'frontend', 'backend', 'docker', 'database', 'server', 'wallet-ui'}
    present = {entry.name.lower() for entry in ROOT.iterdir() if entry.is_dir()}
    if forbidden & present:
        fail('forbidden application artefact directory present: ' + repr(sorted(forbidden & present)))
    tracked = subprocess.run(
        ['git', 'ls-files'], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    if any(path == '.env' or (path.startswith('.env.') and path != '.env.example')
           for path in tracked):
        fail('environment secret file is tracked')
    print('CourseLock source consistency: passed')


if __name__ == '__main__':
    main()
