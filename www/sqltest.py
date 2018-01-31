#-*- coding: utf8 -*-

import orm
import asyncio
from models import User,Blog,Comment

loop = asyncio.get_event_loop()
async def test(loop):
	await orm.create_pool(loop=loop,user='juntian',password='Juntian2008!',db='awesome')
	u = User(id='0015161091377995caa498e4e714b51a79edd3faba076f7000',name='test4444',email='test3test@example.com',passwd='12345678',image='about:blank')
	await u.findNumber('name,email')
	#cur = u.findAll()


#loop.run_until_complete(orm.create_pool(loop=loop,user='juntian',password='Juntian2008!',db='awesome'))

#rs = loop.run_until_complete(orm.select('select * from users where name = \'test\'',None))


rs=loop.run_until_complete(test(loop))

print('hen:%s' % rs)
