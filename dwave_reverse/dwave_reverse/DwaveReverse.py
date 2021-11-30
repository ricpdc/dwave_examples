'''
Created on 22 nov 2021

@author: Alarcos
'''

import sys
import inspect
import linecache
from matplotlib.mathtext import math_to_image
import os


from datetime import datetime
from dimod import utilities



class DwaveReverse(object):
    '''
    Dwave script for reversing hamiltonian from Dwave main annealers functions
    '''
    
    IMG_FOLDER = ("./hamiltonian_expressions") 


    def __init__(self):
        '''
        Constructor
        '''
        self.lastframe = None

    
    @staticmethod
    def quboToH(Q, name):
        H = r'$\mathrm{H='
        first = True
        
        for pair in Q[0]:                    
            if Q[0][pair] == 0:
                continue
            if not first and Q[0][pair] > 0:
                H += '+'
            first = False      
            H += ('' + str(Q[0][pair]) + " \cdot ")                 
            if pair[0] == pair[1]:
                H += (str(pair[0]).lower())
            else:
                H += (' \cdot '.join(pair).lower())
        
        H += (("+" if Q[1]>0 else "") + str(Q[1]))
        
        H += '}$'
                  
                  
                  
        if not os.path.isdir(DwaveReverse.IMG_FOLDER):
            os.makedirs(DwaveReverse.IMG_FOLDER)
         
        math_to_image(H, DwaveReverse.IMG_FOLDER+"/"+name+".png", dpi=300, format='png')
        return H; 
    
   
    # sample in dimod
    @staticmethod
    def getQfromBQM (vars):
        bqm = vars['bqm']
        Q = bqm.to_qubo()
        return Q
       
    # sample_qubo in dwave
    @staticmethod
    def getQfromTupleWithoutOffset(vars):  
        Q = (vars['Q'], 0)
        return Q
    
    # sample_ising in dimod
    @staticmethod
    def getQfromIsing (vars):
        h = vars['h']
        J = vars['J']
        print(h)
        print(J)
        
        Q = utilities.ising_to_qubo(h, J, 0);
        print(Q)
        #Q = bqm.to_qubo()
        return Q
    
    @staticmethod
    def getQ(function, vars):
        
        Q = function(vars)
        return Q

    @staticmethod
    def traceit(frame, event, arg):
        function_code = frame.f_code
        function_name = function_code.co_name
        lineno = frame.f_lineno
        vars = frame.f_locals
        
        
        # if event == 'line':
        #     lineno = frame.f_lineno
        #     filename = frame.f_globals["__file__"]
        #     if filename == "<stdin>":
        #         filename = "traceit.py"
        #     if (filename.endswith(".pyc") or
        #         filename.endswith(".pyo")):
        #         filename = filename[:-1]
        #     name = frame.f_globals["__name__"]
        #     line = linecache.getline(filename, lineno)
        #     print ('{}:{}:{} {}'.format(name,  lineno, frame.f_code.co_name , line.rstrip()))
        
        if event == 'call':
            
            
            trace_name = (vars['self'].__class__.__qualname__ if 'self' in vars.keys() else '') + "." + function_name + "." + str(frame.f_lineno) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            #print(trace_name);
            
            Q = None
            
            if frame.f_code.co_name in ('sample', ) and vars['self'].__class__.__module__.__contains__("dimod"):
                Q = DwaveReverse.getQ(DwaveReverse.getQfromBQM, vars)
            elif frame.f_code.co_name in ('sample_qubo', ) and vars['self'].__class__.__module__.__contains__("dwave"):
                Q = DwaveReverse.getQ(DwaveReverse.getQfromTupleWithoutOffset, vars)
            elif frame.f_code.co_name in ('sample_ising', ) and vars['self'].__class__.__module__.__contains__("dwave"):
                Q = DwaveReverse.getQ(DwaveReverse.getQfromIsing, vars)
            
            
            if Q is not None:
                H = DwaveReverse.quboToH(Q, trace_name);
                print(H);
            # else:
            #     source_lines, starting_line_no = inspect.getsourcelines(frame.f_code)
            #     loc = f"{function_name}:{lineno} {source_lines[lineno - starting_line_no].rstrip()}"
            #     vars = ", ".join(f"{name} = {vars[name]}" for name in vars)
            #     print(f"{loc:80} ({vars})")
        return DwaveReverse.traceit

