# Advanced Python

## Classes and Objects

Everything in python is an object!

```python
>>> s = 'Hello World!'
>>> type(s)
str
>>> help(str)
class str(object)
 |  str(object='') -> str
 |  str(bytes_or_buffer[, encoding[, errors]]) -> str
```

You can see from the documentation that the built-in type str is a class.
When you call a class using parentheses it calls a special method within the class called the constructor.
The constructor returns an object which is an instance of the class.

```python
>>> s = str('Hello World!')
>>> type(s)
str
>>> s
'Hello World!'
>>> str()
''
>>> str(1.0)
'1.0'
```

And you can see that all `str` objects (instances of a `str` `class`) have those string methods that you have used before. Methods are just functions within a class. We use the dot syntax to specify a method within a class, just like we specify a function within a module.


```python
>>> s.lower()
hello world!
>>> s.split()
['Hello', 'World!']
```

The built in function `dir` can help you discover other methods within any object you want to play with.

```python
>>> dir(s)
['__add__',
 '__class__',
 '__contains__',
 '__delattr__',
 '__dir__',
 '__doc__',
 '__eq__',
 '__format__',
 '__ge__',
 '__getattribute__',
 '__getitem__',
 '__getnewargs__',
 '__gt__',
 '__hash__',
 '__init__',
...
]
```

Notice the "dunder" (double underscore) methods? You can use hidden methods like any other function or method.
The constructor method (function within a class) for any class is called `__init__`. Since everything in python is an object even built-in types like `str`, `float`, `int`, and `dict` all have constructors.
The double underscores ("dunder") at the beginning and end of the constructor method just mean that it's a hidden system method.

```python
>>> s = str.__init__('Hello')
>>> s
'Hello'
```

Your first class definition:


```python
>>> class MyNewClass:
...     pass
```

Now let's use that definition to construct an instace of type MyNewClass.


```python
>>> x = MyNewClass()
>>> type(x)
<MyNewClass object 0x123455ABC>
>>> dir(x)
>>> vars(x)
>>> type('')
<str object 0x12345>
>>> def my_new_function(x=None):
...     x = int(x)
...     y = 'Hello World' + str(x)
...     return y
>>> my_new_function()
'Hello WorldNone'
>>> my_new_function(5)
'Hello World5'
```
