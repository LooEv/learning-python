# -*- coding:utf8 -*-

"""
压缩文件工具
使用方法以及其他相关说明：
    1、指定存放需要压缩的文件的文件夹（compress_from_dir）
    2、支持两种压缩方式： bz2, gz， 默认是bz2
    3、压缩后文件存储路径为： compress_from_dir / compressed_data_dir
    4、支持配置匹配哪些子文件和子文件夹能被压缩（正则表达式匹配文件名或者文件夹名）
    5、不会处理改动时间在一分钟以内的文件或者文件夹，以防出现压缩数据不完整的情况
    6、多进程压缩文件
    7、文件压缩时，文件名为*.compressing,压缩完毕后重命名为 *.tar.bz2
"""

import argparse
import os
import re
import tarfile
import time
import traceback

from multiprocessing import cpu_count, Manager
from multiprocessing.pool import Pool
from queue import Empty as QueueEmptyError
from contextlib import suppress
from pathlib import Path

try:
    import commands as exec_command
except ImportError:
    import subprocess as exec_command


def execute_cmd(command):
    try:
        # if execute command succeeded, return 0, else non-zero.
        status, data = exec_command.getstatusoutput(command)
    except Exception as e:
        status, data = 1, str(e)
    return status, data


def check_compress_proc_is_alive():
    file_name = Path(__file__).name
    cmd = 'ps -aux|grep "%s"|grep -v grep|awk \'{print $2}\'' % file_name
    status, data = execute_cmd(cmd)
    if not status and data:
        if len(data.split('\n')) > 1:
            print("compressing process is alive, so don't starting a new one")
            return True
    return False


class PathUtils:
    def __init__(self, compress_from_dir='.', compress_dir_match=None,
                 compress_file_match=None, compress_method='bz2', **kwargs):
        self.compress_target_dir = Path(compress_from_dir)
        self.compress_file_suffix = '.tar.' + compress_method

        if compress_dir_match is not None:
            self._compress_dir_match = re.compile(compress_dir_match)
        else:
            self._compress_dir_match = None

        if compress_file_match is not None:
            self._compress_file_match = re.compile(compress_file_match)
        else:
            self._compress_file_match = None

        self.compressed_data_dir = self.compress_target_dir / 'bbd_compressed_data_dir'
        self.compressed_data_dir.mkdir(exist_ok=True)

    def get_compressed_file_list(self):
        for item in self.compressed_data_dir.glob('*.compressing'):
            with suppress(FileNotFoundError):
                os.remove(str(item.absolute()))

        compressed_file_list = []
        endswith_tuple = (self.compress_file_suffix, self.compress_file_suffix + '__done')
        for item in self.compressed_data_dir.iterdir():
            if item.is_file():
                if item.name.endswith(endswith_tuple):
                    file_name = item.name.rsplit(endswith_tuple[0], 1)[0]
                    compressed_file_list.append(file_name)
        return compressed_file_list

    def match_need_compress_files(self):
        compressed_file_list = self.get_compressed_file_list()
        compressed_file_list.append(self.compressed_data_dir.name)
        for item in self.compress_target_dir.iterdir():
            if item.name in compressed_file_list:
                continue

            if item.is_file() and not self._is_modified_within(item, 60):
                if not self._compress_file_match:
                    yield item
                elif self._compress_file_match.search(item.name):
                    yield item

            elif item.is_dir():
                if self._check_dir_is_modifying(item):
                    continue
                if not self._compress_dir_match:
                    yield item
                elif self._compress_dir_match.search(item.name):
                    yield item

    def _check_dir_is_modifying(self, directory: Path):
        for item in directory.iterdir():
            if self._is_modified_within(item, 60):
                return True
            if item.is_dir():
                return self._check_dir_is_modifying(item)
        return False

    def _is_modified_within(self, file_path: Path, seconds=60):
        now = time.time()
        mtime = file_path.stat().st_mtime
        if now - mtime < seconds:
            print('file: {} may be modifying, '
                  'waiting for next compressing'.format(str(file_path.absolute())))
            return True
        return False


def compress_file(compressed_queue=None):
    assert compressed_queue is not None
    try:
        while not compressed_queue.empty():
            from_path, to_path, mode = compressed_queue.get(False)
            compressing_filename = to_path + '.compressing'
            print('compressing file: %s' % from_path)
            tar = tarfile.open(compressing_filename, 'w:' + mode)
            tar.add(from_path, arcname=os.path.basename(from_path))
            tar.close()
            print(from_path, '...done')
            os.rename(compressing_filename, to_path + '.tar.{}'.format(mode))
    except QueueEmptyError:
        pass
    except Exception:
        print('compress error:', traceback.format_exc())


def compress_file(compressed_queue=None, compress_method='bz2', **kwargs):
    assert compressed_queue is not None
    compress_to_dir = kwargs['compress_to_dir']
    compress_from_dir = kwargs['compress_from_dir']
    try:
        while not compressed_queue.empty():
            file_list = compressed_queue.get(False)
            compressing_filename = 'flume_data_' + get_timestamp_and_pid() \
                                   + '.tar.%s' % compress_method
            compressing_file_path = os.path.join(compress_from_dir, compressing_filename)
            tar = tarfile.open(compressing_file_path, 'w:' + compress_method)
            for file in file_list:
                print('compressing file: %s' % file)
                tar.add(file, arcname=os.path.basename(file))
            tar.close()
            # rm_files(file_list)
            dst = os.path.join(compress_to_dir, compressing_filename)
            print(compressing_file_path, dst)
            shutil.move(compressing_file_path, dst)
    except QueueEmptyError:
        pass
    except Exception:
        print('compress error:', traceback.format_exc())


def multi_workers(max_worker=cpu_count(), pool_cls=Pool, work=None, **kwargs):
    pool = pool_cls(max_worker)
    [pool.apply_async(work, kwds=kwargs) for _ in range(max_worker)]
    pool.close()
    pool.join()


def main():
    arg_parser = argparse.ArgumentParser(description='bbd compressing program')
    arg_parser.add_argument('-compress_from_dir', type=str, default='.',
                            help='directory where needs to be compressed')
    arg_parser.add_argument('-compress_to_dir', type=str, default='.',
                            help='directory where puts compressed file')
    arg_parser.add_argument('-compress_method', default='bz2', choices=['bz2', 'gz'],
                            help='the method of compressing, '
                                 'support bz2 and gz, bz2 is default')
    arg_parser.add_argument('-compress_dir_match', default=None,
                            help='regular expressions what matches '
                                 'which directories can be compressed')
    arg_parser.add_argument('-compress_file_match', default=None,
                            help='regular expressions what matches '
                                 'which files can be compressed')

    args = arg_parser.parse_args()
    kwargs = dict()
    kwargs['compress_from_dir'] = os.path.abspath(args.compress_from_dir)
    kwargs['compress_to_dir'] = os.path.abspath(args.compress_to_dir)
    kwargs['compress_method'] = args.compress_method
    kwargs['compress_dir_match'] = args.compress_dir_match
    kwargs['compress_file_match'] = args.compress_file_match
    print('Operating parameters are as follows:')
    print('\t' + '\n\t'.join(['{}: {}'.format(k, v) for k, v in kwargs.items()]))

    if check_compress_proc_is_alive():
        return

    if kwargs['compress_from_dir'] == kwargs['compress_to_dir']:
        print(kwargs['compress_from_dir'], kwargs['compress_to_dir'])
        compress_to_dir = os.path.join(kwargs['compress_to_dir'], 'flume_compressed_data')
        kwargs['compress_to_dir'] = compress_to_dir
        os.makedirs(compress_to_dir, exist_ok=True)

    max_worker = cpu_count() if cpu_count() <= 8 else 8
    pool_cls = Pool
    compressed_queue = Manager().Queue()
    print('using multi processes to compress files')

    path_mgr = PathUtils(**kwargs)
    compressed_data_dir = Path(kwargs['target_dir']) / 'bbd_compressed_data_dir'
    compress_method = kwargs['compress_method']
    for file_path in path_mgr.match_need_compress_files():
        from_path = str(file_path.absolute())
        to_path = str((compressed_data_dir / file_path.name).absolute())
        compressed_queue.put((from_path, to_path, compress_method))

    if compressed_queue.empty():
        print('there is no file need to be compressed, waiting for next checking')
        return

    multi_workers(max_worker=max_worker, pool_cls=pool_cls, work=compress_file,
                  compressed_queue=compressed_queue)


if __name__ == '__main__':
    main()
