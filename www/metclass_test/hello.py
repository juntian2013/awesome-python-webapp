#_*_ coding: utf-8 _*_

def fn(self,name='world'):
	print('Hello,%s.' % name)

#create the class to create class
Hello = type('Hello',(object,),dict(hello=fn)) #create Hello class

h = Hello()
print('call h.hello():')
h.hello()
print('type(Hello) =',type(Hello))
print('type(h) = ',type(h))
