import os
import tarfile

from multiprocessing import cpu_count, Pool
from pathlib import Path


def get_file_size(file_path: str):
    file = Path(file_path)
    return file.stat().st_size  # the bytes size of a file


def file_is_in_dir(dir_path, file_path):
    dir_path = Path(dir_path).resolve()
    file = Path(file_path).resolve()
    if file.exists() and file.is_file():
        if str(file).startswith(str(dir_path)):
            # file is in dir_path
            return True
    # raise FileNotFoundError("can't find the file of %s" % file_path)
    return False


def compress_file(from_path='.', to_path='.', mode='bz2'):
    if not os.path.isabs(from_path):
        from_path = os.path.abspath(from_path)
    if not os.path.isabs(to_path):
        to_path = os.path.abspath(to_path)
    compressed_filename = os.path.join(to_path, '.tar.%s' % mode)
    print('compressing file: %s' % from_path, end=' ')
    tar = tarfile.open(compressed_filename, 'w:' + mode)
    tar.add(from_path, arcname=os.path.basename(from_path))
    tar.close()
    print(from_path, '...done')


def multi_workers(max_worker=cpu_count(), pool_cls=Pool, work=None, **kwargs):
    pool = pool_cls(max_worker)
    [pool.apply_async(work, kwds=kwargs) for _ in range(max_worker)]
    pool.close()
    pool.join()
