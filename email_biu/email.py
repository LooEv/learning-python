import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, parseaddr

try:
    from ConfigParser import ConfigParser  # python2
except ImportError:
    from configparser import ConfigParser  # python3

try:
    from urllib.parse import quote  # python3
except ImportError:
    from urllib import quote  # python2


def format_email_header(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def generate_email_msg(content, message_type=None):
    now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
    file_size_warning = ''
    if os.path.isfile(log_file):
        if (os.path.getsize(log_file) / 1024.0 / 1024.0) > 200:
            file_size_warning = u'温馨提示：脚本日志文件过大，建议删除。'
    if message_type == 'comment':
        me_header = u'多说评论提醒'
        sub = u'新评论提醒{0}'
        _subtype = 'html'
        content = u'<html><body>{0}<p>{1}</p></body></html>'.format(content, file_size_warning)
    else:
        # when message_type is 'log'
        me_header = u'Comment notifier日志'
        sub = u'脚本出现错误{0}'
        _subtype = 'plain'
        content = content + '\n' + file_size_warning
    me = me_header + '<' + config['from_address'] + '>'
    msg = MIMEText(content, _subtype=_subtype, _charset='utf-8')
    msg['Subject'] = Header(sub.format(now), 'utf-8').encode()
    msg['From'] = format_email_header(me)
    msg['To'] = config['to_address']
    return msg


def send_email(content, message_type=None):
    msg = generate_email_msg(content, message_type)
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(config['email_host'])
        server.login(config['from_address'], config['email_password'])
        server.sendmail(config['from_address'], config['to_address'], msg.as_string())
        logger.debug(u'{0}邮件发送成功'.format(u'评论提醒' if message_type == 'comment' else u'日志提醒'))
        server.quit()
    except Exception as e:
        logger.exception(e)
        logger.error(u'邮件发送失败！')
