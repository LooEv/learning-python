import subprocess

def execute_cmd(command):
    try:
        # if execute command succeeded, return 0, else non-zero.
        status, data = subprocess.getstatusoutput(command)
    except Exception as e:
        status, data = 1, str(e)
    return status, data

def check_process_is_alive(process_info):
    cmd = 'ps -aux|grep "%s"|grep -v grep|awk \'{print $2}\'' % process_info
    status, data = execute_cmd(cmd)
    if not status and data:
        if len(data.split('\n')) > 1:
            print("compressing process is alive, so don't starting a new one")
            return True
    return False


if __name__ == '__main__':
    print(check_process_is_alive('server.py'))
