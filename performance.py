#To give the timeit module access to functions you define, you can pass a setup parameter which contains an import statement:
def test():
    """Stupid test function"""
    L = [i for i in range(100)]
    print(L)

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("test()", setup="from __main__ import test"))





#Another option is to pass globals() to the globals parameter, which will cause the code to be executed within your current global namespace. This can be more convenient than individually specifying imports:

def f(x):
    return x**2
def g(x):
    return x**4
def h(x):
    return x**8

if __name__ == '__main__':
   import timeit
   print(timeit.timeit('[func(42) for func in (f,g,h)]', globals=globals()))





#It is possible to provide a setup statement that is executed only once at the beginning:
if __name__ == '__main__':
   import timeit
   timeit.timeit('char in text', setup='text = "sample string"; char = "g"')
   #0.41440500499993504
   timeit.timeit('text.find(char)', setup='text = "sample string"; char = "g"')
   #1.7246671520006203

#The same can be done using the Timer class and its methods:
if __name__ == '__main__':
   import timeit
   t = timeit.Timer('char in text', setup='text = "sample string"; char = "g"')
   t.timeit()
   #0.3955516149999312
   t.repeat()
   #[0.40193588800002544, 0.3960157959998014, 0.39594301399984033]

