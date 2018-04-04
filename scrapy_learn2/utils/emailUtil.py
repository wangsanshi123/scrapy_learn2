# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# 第三方 SMTP 服务
# # mail_host = "smtp.163.com"  # 设置服务器
# mail_host = "smtp.qq.com"  # 设置服务器
# # mail_user = "13135767989@163.com"  # 用户名
# count = "1183195926@qq.com"  # 用户名
# # mail_pass = "4833123yuan"  # 口令
# password = "jvwcweisuiipgfdd"  # 口令
#
# # sender = '13135767989@163.com'
# sender = '1183195926@qq.com'
#
# receivers = ['1183195926@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱


config_QQ = {
    "mail_host": "smtp.qq.com",
    "count": "1183195926@qq.com",
    "password": "jvwcweisuiipgfdd",
    "sender": "1183195926@qq.com",
    "receivers": ['1183195926@qq.com', 'yuantaixing@126.com'],
}
config_163 = {
    "mail_host": "smtp.163.com",
    "count": "13135767989@163.com",
    "password": "4833123yuan",
    "sender": "13135767989@163.com",
    "receivers": ['1183195926@qq.com', 'yuantaixing@126.com'],
}


def setMsg(topic=u'您好', content='Hello World', config=None):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = formataddr(["ytx-python", config['sender']])
    message['To'] = formataddr(["FK", config['receivers']])
    message['Subject'] = topic
    return message


def sendMsg_163(config=config_163, info=u'任务结束'):
    msg = setMsg(topic=u'任务结束',
                 content=info,
                 config=config_163)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(config['mail_host'], 25)  # 25 为 SMTP 端口号
        smtpObj.login(config['count'], config['password'])
        smtpObj.sendmail(config['sender'], config['receivers'], msg.as_string())
        print u"发送成功"
    except Exception, e:
        print e
        print u"\n发送失败"
        pass


def sendMsg_QQ(config=config_QQ, info=u'任务结束'):
    msg = setMsg(topic=u'任务结束',
                 content=info, config=config_QQ)

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(config['sender'], config['password'])  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(config['sender'], config['receivers'], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print u'发送消息成功'
    except Exception, e:
        print u'发送消息失败'
        print e
        pass


if __name__ == '__main__':
    sendMsg_QQ(config_QQ)
