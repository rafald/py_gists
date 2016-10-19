/tmp/$ mkdir test; cd test
/tmp/test/$ mkdir foo; mkdir bar
/tmp/test/$ echo -e "foo\nbar" > foobar.pth
/tmp/test/$ cd ..
/tmp/$ python

Python 2.6 (r26:66714, Feb  3 2009, 20:52:03)
[GCC 4.3.2 [gcc-4_3-branch revision 141291]] on linux2
Type "help", "copyright", "credits" or "license" for more information.

>>> import site, sys
>>> site.addsitedir('test')
>>> sys.path[-3:]
['/tmp/test', '/tmp/test/foo', '/tmp/test/bar']
