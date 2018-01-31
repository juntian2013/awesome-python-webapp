#-*- coding -*-

from coroweb import get
from models import User
import asyncio

@get('/')
async def index(request):
	users = await User.findAll()
	#print(users)
	return {'__template__':'test.html','users':users}

@get('/hello')
async def hello(request):
	return '<h1>hello!</h1>'
