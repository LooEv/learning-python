#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
@File    : download_file_bridge.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-01 23:18:26
@History :
@Desc    : 
"""

import argparse
import os
import warnings

from contextlib import suppress

import paramiko

warnings.filterwarnings(action='ignore', module='paramiko')


class MySSHClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = password

    def connect_server(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, self.port, self.username, self.pwd)

    def exec_remote_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        # print(stdout.read().decode())

    def wget_file(self, remote_file_dir, file_name, file_url):
        remote_file = f'{remote_file_dir}/{file_name}'
        cmd = f'wget -O {remote_file} "{file_url}"'
        print(f'start to execute: {cmd}')
        with suppress(OSError):
            self.ssh_client.exec_command(f'mkdir -p {remote_file_dir}')
        self.exec_remote_cmd(cmd)
        print(f'success to get {file_url}')

    def get_file(self, remote_file, local_file):
        local_file = os.path.expanduser(local_file)
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        sftp_client = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())
        print(f'get {remote_file} to {local_file}')
        sftp_client.get(remote_file, local_file)
        print('done')

    def close(self):
        self.ssh_client.close()


def main():
    arg_parser = argparse.ArgumentParser(description='using remote server as a bridge to download a file')
    arg_parser.add_argument('-host', type=str)
    arg_parser.add_argument('-port', type=int)
    arg_parser.add_argument('-user', type=str)
    arg_parser.add_argument('-password', type=str)
    arg_parser.add_argument('-file_url', type=str)
    arg_parser.add_argument('-file_name', type=str)

    args = arg_parser.parse_args()
    ssh_client = MySSHClient(args.host, args.port, args.user, args.password)
    ssh_client.connect_server()
    if args.user == 'root':
        remote_file_dir = '/root/temp_data'
    else:
        remote_file_dir = f'/home/{args.user}/temp_data'
    ssh_client.wget_file(remote_file_dir, args.file_name, args.file_url)
    ssh_client.get_file(f'{remote_file_dir}/{args.file_name}', f'~/temp_data/{args.file_name}')
    ssh_client.close()


if __name__ == '__main__':
    main()
