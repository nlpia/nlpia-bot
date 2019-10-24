# data_science_exercise_python_classes_and_objects.md

```python
>>> class MyNewClass:
...     pass

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
