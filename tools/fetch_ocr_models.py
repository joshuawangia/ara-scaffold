"""Explicit one-time download of pinned public weights; never reads PDFs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tarfile
import tempfile
from urllib.request import urlopen
import shutil

from ara.runtime.ocr import LOCK, verify_models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('cache/ocr'))
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    lock = json.loads(LOCK.read_text())
    for name, model in lock.items():
        try:
            verify_models(args.cache, {name: model})
            continue
        except ValueError:
            pass
        with tempfile.TemporaryDirectory(dir=args.cache) as temporary:
            root = Path(temporary)
            archive = root / 'model.tar'
            with urlopen(model['url'], timeout=120) as source, archive.open('wb') as destination:
                shutil.copyfileobj(source, destination)
            if sha256(archive.read_bytes()).hexdigest() != model['archive_sha256']:
                raise ValueError('downloaded OCR archive hash mismatch')
            with tarfile.open(archive) as bundle:
                bundle.extractall(root, filter='data')
            verify_models(root, {name: model})
            for filename in model['files']:
                target = args.cache / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                (root / filename).replace(target)
        print(f'{name}: verified')
    verify_models(args.cache, lock)


if __name__ == '__main__':
    main()
