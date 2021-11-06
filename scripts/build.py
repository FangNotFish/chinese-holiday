import glob
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import tarfile
import zipfile

BASE_DIR = pathlib.Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "dataset"
DIST_DIR = BASE_DIR / ".dist"


def _describe():
    '''returns a string which is the identifier of this build'''
    try:
        ret = subprocess.run(
            ['git', 'describe', '--always'],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return datetime.date.today().strftime('%y-%m-%d')
    else:
        return ret.stdout.decode().strip()


def _basename():
    '''returns basename of build target, include parent path'''
    basename = 'chinese-holiday'
    tag = _describe()
    if tag:
        basename += '-' + tag

    if not os.path.exists(DIST_DIR):
        os.mkdir(DIST_DIR)

    return basename


def _load_json(fn):
    with open(fn, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(fn, data):
    with open(fn, "w", encoding="utf-8") as f:
        return json.dump(data, f)


def _sha512_hash(fn):
    with open(fn, 'rb') as f:
        hash = hashlib.sha512(f.read())

    with open(str(fn) + ".sha512", "w", encoding="utf-8") as f:
        f.write(hash.hexdigest())


def zip(files, dest):
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for file in files:
            zip_file.write(file, arcname=os.path.basename(file))
        return zip_file.filename


def gz_tar(files, dest):
    with tarfile.TarFile.open(dest, "w:gz") as tar_file:
        for file in files:
            tar_file.add(file, arcname=os.path.basename(file))
        return tar_file.name


def merge(files, dest):
    merged = []
    for fn in files:
        merged.append(_load_json(fn))

    _dump_json(dest, merged)
    return dest


def build():
    basename = _basename()

    dataset_files = glob.glob(str(DATASET_DIR/"*.json"))
    files = dataset_files + [str(BASE_DIR / "LICENSE")]

    archives = [
        zip(files, DIST_DIR / (basename + '.zip')),
        gz_tar(files, DIST_DIR / (basename + '.tar.gz')),
        merge(dataset_files, DIST_DIR / (basename + '.json')),
    ]

    [_sha512_hash(archive) for archive in archives]


if __name__ == '__main__':
    build()
