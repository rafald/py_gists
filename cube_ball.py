#!/usr/bin/env python

from scipy.special import gamma
from math import pi

def unit_sphere_volume(n): 
	return pi**(0.5*n)/gamma(0.5*n + 1)

def unit_cube_volume(n): 
	return 2**n

def ratio(n):
	return unit_sphere_volume(n) / unit_cube_volume(n)

print( [ratio(n) for n in range(1, 20)] )

