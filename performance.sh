
#It is possible to provide a setup statement that is executed only once at the beginning:
python -m timeit -s 'text = "sample string"; char = "g"'  'char in text'
#10000000 loops, best of 3: 0.0877 usec per loop
python -m timeit -s 'text = "sample string"; char = "g"'  'text.find(char)'
#1000000 loops, best of 3: 0.342 usec per loop


#The following examples show how to time expressions that contain multiple lines. Here we compare the cost of using hasattr() vs. try/except to test for missing and present object attributes:

python -m timeit 'try:' '  str.__bool__' 'except AttributeError:' '  pass'
#100000 loops, best of 3: 15.7 usec per loop
python -m timeit 'if hasattr(str, "__bool__"): pass'
#100000 loops, best of 3: 4.26 usec per loop

python -m timeit 'try:' '  int.__bool__' 'except AttributeError:' '  pass'
#1000000 loops, best of 3: 1.43 usec per loop
python -m timeit 'if hasattr(int, "__bool__"): pass'
#100000 loops, best of 3: 2.23 usec per loop

