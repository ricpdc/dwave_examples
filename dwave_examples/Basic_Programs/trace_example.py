'''
Created on 15 nov 2021

@author: Alarcos
'''


import sys
import inspect

import matplotlib.pyplot as plt
from matplotlib.mathtext import math_to_image
 
from sympy import *

import xml.dom.minidom
import re


def factorial(num):
    i=1
    result = 1
    while(i <= num):
        result *= i
        i+=1
    return result
'''
def traceit(frame, event, arg):
    if event == 'call' and frame.f_code.co_name in ('schedule_cb', ):
        
        print("line %s code %s", frame.f_lineno, frame.f_code.co_name, frame.f_code.co_name)
    

    return traceit
''' 
 
 
def traceit(frame, event, arg):
    function_code = frame.f_code
    function_name = function_code.co_name
    lineno = frame.f_lineno
    vars = frame.f_locals

    source_lines, starting_line_no = inspect.getsourcelines(frame.f_code)
    loc = f"{function_name}:{lineno} {source_lines[lineno - starting_line_no].rstrip()}"
    vars = ", ".join(f"{name} = {vars[name]}" for name in vars)

    print(f"{loc:50} ({vars})")

    return traceit

    
 
exp = r'$\sum_{i=0}^\infty x_i$'

exp = r'$\mathit{H=1 \cdot B+1 \cdot K+2 \cdot A \cdot C-2 \cdot A \cdot K-2 \cdot B \cdot C}$'


math_to_image(exp, "test.svg", dpi=300, format='svg')
math_to_image(exp, "test.png", dpi=300, format='png')


print("\n5!=",factorial(5))

H, a, b, c, k = symbols('H a b c k')
init_printing(use_unicode=True)

H = '-2.0*a*k-2.0*c*b+2.0*c*a+1.0*b+1.0*k+1.0'

H=H.replace('a', '(1-a)')
H=H.replace('b', '(1-b)')
H=H.replace('c', '(1-c)')
H=H.replace('k', '(1-k)')

print(H)


print(factor(H))


file = './kdm/general_program_qubo.py.kdm'

pretty_xml_as_string = xml.dom.minidom.parse(file).toprettyxml()
        
print('\n\n\nBEFORE\n\n\n' + pretty_xml_as_string)

z = re.match(r"(\n\t+)+",  pretty_xml_as_string)

if z:
    print('Found a match!')
    print((z.groups()))
    

pretty_xml_as_string = re.sub(r"(\n\t+)+", "", pretty_xml_as_string)
pretty_xml_as_string = re.sub(r"\n", "", pretty_xml_as_string)

print('\n\n\nAFTER\n\n\n' + pretty_xml_as_string)

open(file, "w+", newline='', encoding='utf-8').write(pretty_xml_as_string)






