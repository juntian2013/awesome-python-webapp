from aiohttp import web
import asyncio

TODOS = [{'name':'Start this tutorial','finished':True},{'name':'Finish this tutorial','finished':False}]

def get_all_todos(request):
	return web.json_response([{'id':idx,**todo} for idx,todo in enumerate(TODOS)])

def get_one_todo(request):
	id = int(request.match_info['id'])
	print(request.match_info)
	if id >= len(TODOS):
		return web.json_response({'error':'Todo not found'},status='404')
	return web.json_response({'id':id,**TODOS[id]})

async def create_todo(request):
	data = await request.json()

	if 'name' not in data:
		return web.json_response({'error':'"name" is a required field'})
	name = data.get('name')

	if not isinstance(name,str) or not len(name):
		return web.json_response({'error':'"name" must be a string with at least one character'})

	data['finished'] = bool(data.get('finished',False))
	TODOS.append(data)
	new_id = len(TODOS) - 1
	return web.Response(headers = {'Location':str(request.app.router['one_todo'].url_for(id=new_id))},status=303)

async def update_todo(request):
	id = int(request.match_info['id'])
	if id >= len(TODOS):
		return web.json_response({'error':'Todo not found'},status=404)
	data = await request.json()

	if 'finished' not in data:
		return web.json_response({'error':'"finished" is a required key'},status=400)

	TODOS[id]['finished'] = bool(data['finished'])

	return web.Response(status=204)

def remove_todo(request):
	id = int(request.match_info['id'])

	if id >= len(TODOS):
		return web.json_response({'error':'Todo not found'})

	del TODOS[id]
	return web.Response(status=204)

def app_factory(args=()):
	app = web.Application()
	app.router.add_get('/todos/',get_all_todos,name='all_todos')
	app.router.add_post('/todos/',create_todo,name='create_todo',expect_handler=web.Request.json)
	app.router.add_get('/todos/{id:\d+}',get_one_todo,name='one_todo')
	app.router.add_patch('/todos/{id:\d+}',update_todo,name='update_todo')
	app.router.add_delete('/todos/{id:\d+}',remove_todo,name='remove_todo')
	return app
