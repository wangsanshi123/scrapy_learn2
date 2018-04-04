# -*- coding: utf-8 -*-
# @Time : 2017/1/1 17:51
# @Author : woodenrobot
from scrapy import cmdline

name = 'stocks'
# name = 'cnblogs'
# name = 'cforum'
# name = 'test1'
# name = 'test2'
# name = 'gsmarena'
# name = 'getips_2'
# name = 'cforum_reply'
# name = 'gsmarena_2'
name = 'gsmarenainfo'
name = 'gsmarenacomments'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())
