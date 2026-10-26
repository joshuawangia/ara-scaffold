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
    parser.add_argument('--vl', action='store_true', help='also fetch pinned official VL weights')
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
    if args.vl:
        fetch_vl(args.cache)


def fetch_vl(cache):
    from ara.runtime.ocr_vl import VL_LOCK, verify_vl_model
    from hashlib import file_digest
    lock = json.loads(VL_LOCK.read_text())
    root = cache / 'PaddleOCR-VL-1.6'
    root.mkdir(parents=True, exist_ok=True)
    for filename, expected in lock['files'].items():
        target = root / filename
        if target.is_file():
            with target.open('rb') as stream:
                if file_digest(stream, 'sha256').hexdigest() == expected['sha256']:
                    continue
        url = f"https://huggingface.co/{lock['repo']}/resolve/{lock['revision']}/{filename}"
        with tempfile.TemporaryDirectory(dir=root) as temporary:
            download = Path(temporary) / 'download'
            with urlopen(url, timeout=120) as source, download.open('wb') as destination:
                shutil.copyfileobj(source, destination)
            with download.open('rb') as stream:
                if file_digest(stream, 'sha256').hexdigest() != expected['sha256']:
                    raise ValueError('downloaded VL file hash mismatch')
            download.replace(target)
    verify_vl_model(cache, lock)
    print('PaddleOCR-VL-1.6: verified')


if __name__ == '__main__':
    main()
