#-*- coding:utf-8 -*-

import logging
import asyncio,os,json,time
from datetime import datetime
from config import configs
from aiohttp import web
from jinja2 import Environment,FileSystemLoader

import orm
from coroweb import add_routes,add_static,add_route

def init_jinja2(app,**kw):
	logging.info('init jinja2')
	options = dict(
	autoescape = kw.get('autoescape',True),
	block_start_string = kw.get('block_start_string','{%'),
	block_end_string = kw.get('block_end_string','%}'),
	variable_start_string = kw.get('variable_start_string','{{'),
	variable_end_string = kw.get('variable_end_string','}}'),
	auto_reload = kw.get('auto_reload',True)
	)

	path = kw.get('path',None)
	if not path:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
	env = Environment(loader = FileSystemLoader(path),**options)

	filters = kw.get('filters',None)
	if filters:
		for name,f in filters.items():
			env.filters[name] = f
	app['__template__'] = env

def datetime_filter(t):
	delta = int(time.time()-t)
	if delta < 60:
		return 'one minute ago'
	if delta < 3600:
		return '%s minutes ago' % (delta//60)
	if delta < 86400:
		return '%s hours ago' % (delta//3600)
	if delta > 604800:
		return '%s day ago' % (delta//86400)
	dt = datetime.fromtimestamp(t)
	return '%s year %s month %s days' % (dt.year,dt.month,dt.day)

async def logger_factory(app,handler):
	async def logger(request):
		logging.info('Reuqest:%s %s' % (request.method,request.path))
		return await handler(request)
	return logger

async def response_factory(app,handler):
	async def response(request):
		logging.info('Response handler...')
		r = await handler(request)
		logging.info('response result = %s' % str(r))
		if isinstance(r,web.StreamResponse):
			return r
		if isinstance(r,bytes):
			logging.info('*'*10)
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp
		if isinstance(r,str):
			if r.startswith('redirect:'):
				return web.HTTPFound(r[9:])
			resp = web.Response(body=r.encode('utf-8'))	
			resp.content_type = 'text/html;charset=utf-8'
			return resp

		if isinstance(r,dict):
			template = r.get('__template__',None)
			if template is None:
				resp = web.Response(body=json.dumps(r,ensure_ascii=False,default = lambda obj:obj.__dict__).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				resp = web.Response(body=app['__template__'].get_template(template).render(**r))
				resp.content_type='text/html;charset=utf-8'
				return resp
		if isinstance(r,int) and (600>r>=100):
			resp = web.Response(status=r)
			return resp
		if isinstance(r,tuple) and len(r) == 2:
			status_code,message=r
			if isinstance(status_code,int) and (600>status_code>=100):
				resp = web.Response(status=r,text=str(message))
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp
	return response


async def init(loop):
	await orm.create_pool(loop=loop,**configs['db'])
	app = web.Application(loop=loop,middlewares=[logger_factory,response_factory])
	init_jinja2(app,filters=dict(datetime=datetime_filter))
	add_routes(app,'test_view')
	add_static(app)
	srv = await loop.create_server(app.make_handler(),'localhost',8000)
	logging.info('serveer started at http://127.0.0.1:8000...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
