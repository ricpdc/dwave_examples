'''
Created on 22 nov 2021

@author: Alarcos
'''

import sys
import inspect
import linecache
from matplotlib.mathtext import math_to_image
import os
from sympy import *
import ntpath
import csv


from datetime import datetime
from dimod import utilities
from dwave_reverse.KDMGenerator import KDMGenerator

from timeit import default_timer as timer



class DwaveReverse(object):
    '''
    Dwave script for reversing hamiltonian from Dwave main annealers functions
    '''
    
    H_FOLDER = ("./hamiltonian_expressions") 
    CSV_FOLDER = ("./metrics") 


    def __init__(self):
        '''
        Constructor
        '''
        self.lastframe = None

    @staticmethod
    def computeMetrics(Q):
        print('\n>>>>#Coefficients: ' + str(len(Q[0])))
        
        variables = []
        for pair in Q[0]:
            if pair[0] not in variables:
                variables.append(pair[0])
            if pair[1] not in variables:
                variables.append(pair[1])
        
        print('\n>>>>#Variables: ' + str(len(variables)))
        print(variables)
        
        #print(Q)
        return variables

    @staticmethod
    def quboToBQM(Q):
        
        H = 'H='
        first = True
        for pair in Q[0]: 
            if Q[0][pair] == 0:
                continue
            if not first and Q[0][pair] > 0:
                H += '+'
            first = False      
            H += ('' + str(Q[0][pair]) + "*")                 
            if pair[0] == pair[1]:
                if isinstance(pair[0], str):
                    H += (str(pair[0]).lower())
                else:
                    H += ('a' + str(pair[0]))
            else:
                if isinstance(pair[0], str):
                    H += ('*'.join(pair).lower())
                else:
                    H += ('a' + str(pair[0]) + '*a' + str(pair[1]))
        H += (("+" + str(Q[1])) if Q[1] > 0 else "")
        
        print(H)
        
        DwaveReverse.computeMetrics(Q)
        
        return H; 
    
    
    
    @staticmethod
    def quboToH(Q):
        
        H = ''
        coefficients = []
        variables = set()
        first = True
        for pair in Q[0]: 
            if Q[0][pair] == 0:
                continue
            if not first and Q[0][pair] > 0:
                H += '+'
            first = False
            
            coeff = Q[0][pair]/2.0
            coefficients.append(coeff)
            H += (str(coeff) + "*")        
                             
            if pair[0] == pair[1]:
                var = str(pair[0]).lower() if isinstance(pair[0], str) else ('a' + str(pair[0]))
                symbols(var)
                variables.add(var) 
                H += '(1-'+var+')'
            else:
                var1 = str(pair[0]).lower() if isinstance(pair[0], str) else ('a' + str(pair[0])) 
                var2 = str(pair[1]).lower() if isinstance(pair[1], str) else ('a' + str(pair[1])) 
                symbols(var1)
                symbols(var2)                
                variables.add(var1)
                variables.add(var2)
                
                H += ('(1-'+var1+')*(1-' + var2+')')
                
        H += (("+" + str(Q[1])) if Q[1] > 0 else "")
        
        
        print("BQM: " + H)
        print('\n>>>>#Coefficients: ' + str(len(coefficients)))
        print(coefficients)
        
        print('\n>>>>#Variables: ' + str(len(variables)))
        print(variables)
        
        H=simplify(H)
        H = 'H = ' + str(H)
        
               
        print(">>>" + H)
        
        
        return H, variables, coefficients; 
    
    
    
    @staticmethod
    def generateHinTextFile(H, name):
        if not os.path.isdir(DwaveReverse.H_FOLDER):
            os.makedirs(DwaveReverse.H_FOLDER)
        
        text_file = open(DwaveReverse.H_FOLDER+"/"+name+".txt", "w+")
        text_file.write(str(H))
         
        text_file.close()
        
    
    @staticmethod
    def generateHinImage(H, name):
        H = str(H)
        H = H.replace('*', ' \cdot ', -1)
        H = r'$\mathrm{' + H + '}$'
        
        if not os.path.isdir(DwaveReverse.H_FOLDER):
            os.makedirs(DwaveReverse.H_FOLDER)
         
        try: 
            math_to_image(H, DwaveReverse.H_FOLDER+"/"+name+".png", dpi=300, format='png')
        except:
            print('Expression to large to be drawn')
        
        return H

   
    @staticmethod
    def saveMetrics(name, metrics):
        if not os.path.isdir(DwaveReverse.CSV_FOLDER):
            os.makedirs(DwaveReverse.CSV_FOLDER)
        header = None
        file_path = DwaveReverse.CSV_FOLDER + '/' + name + '.csv'
        if not os.path.isfile(file_path):
            header = ['class name', 'function name', 'function line', 'type', '#variables', '#coefficients', 'time H text (s)', 'time H image (s)', 'Time H Total (s)', 'Time KDM (s)']
        
        with open(DwaveReverse.CSV_FOLDER+"/"+name+".csv", "a+", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter='\t')
            if header is not None:
                writer.writerow(header)
            writer.writerow(metrics)
            csv_file.close()
        
   
    # sample in dimod
    @staticmethod
    def getQUBOfromBQM (vars):
        bqm = vars['bqm']
        QUBO = bqm.to_qubo()
        return QUBO
       
    # sample_qubo in dwave
    @staticmethod
    def getQUBOfromTupleWithoutOffset(vars):  
        QUBO = (vars['Q'], 0)
        return QUBO
    
    # sample_ising in dimod
    @staticmethod
    def getQUBOfromIsing (vars):
        h = vars['h']
        J = vars['J']
        print(h)
        print(J)
        
        QUBO = utilities.ising_to_qubo(h, J, 0);
        print(QUBO)
        # Q = bqm.to_qubo()
        return QUBO
    
    @staticmethod
    def getQUBO(function, vars):
        
        QUBO = function(vars)
        return QUBO

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
            time_start = timer()
            time = timer()
           
            #trace_name = class_name + "." + function_name + "." + function_line
            #print(trace_name);
            
            QUBO = None
            type = None
            
            if frame.f_code.co_name in ('sample', ):
                print(vars['self'].__class__.__module__)
            
            if frame.f_code.co_name in ('sample', ) and vars['self'].__class__.__module__ in ("dwave.system.composites.embedding", "dwave.system.samplers.leap_hybrid_sampler", "neal.sampler",):
                type = 'QUBO'
                time_start = timer()
                time = timer()
                QUBO = DwaveReverse.getQUBO(DwaveReverse.getQUBOfromBQM, vars)
            elif frame.f_code.co_name in ('sample_qubo', ) and vars['self'].__class__.__module__.__contains__("dwave"):
                type = 'TupleWithoutOffset'
                time_start = timer()
                time = timer()
                QUBO = DwaveReverse.getQUBO(DwaveReverse.getQUBOfromTupleWithoutOffset, vars)
            elif frame.f_code.co_name in ('sample_ising', ) and vars['self'].__class__.__module__.__contains__("dwave"):
                type = 'Ising'
                time_start = timer()
                time = timer()
                QUBO = DwaveReverse.getQUBO(DwaveReverse.getQUBOfromIsing, vars)
            
            
            if QUBO is not None:
                
                class_name = vars['self'].__class__.__qualname__ if 'self' in vars.keys() else ''
                function_line = str(frame.f_lineno)
                trace_name = class_name + "." + function_name + "." + function_line + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                
                H, variables, coefficients = DwaveReverse.quboToH(QUBO)
                time_H = timer()-time
                time = timer()
                print(H)
                              
                DwaveReverse.generateHinTextFile(H, trace_name)
                
                time_H_text = timer()-time
                time = timer()
                
                if len(coefficients) < 150 :
                    Hm = DwaveReverse.generateHinImage(H, trace_name)
                
                time_H_image = timer()-time
                time = timer()
                    
                time_H_total = timer()-time_start
                
                #print('>>>>  H time: ' + str(time_H_total))
                print(H)
                
                time = timer()
                
                KDMGenerator().generateKDM(H, class_name, function_name, function_line)
                time_KDM = timer()-time
                #print('>>>>KDM time: ' + str(time_KDM))
                
                DwaveReverse.saveMetrics(ntpath.basename(sys.argv[0]), [class_name, function_name, function_line, type, len(variables), len(coefficients), time_H_text, time_H_image, time_H_total, time_KDM])
                
                
            # else:
            #     source_lines, starting_line_no = inspect.getsourcelines(frame.f_code)
            #     loc = f"{function_name}:{lineno} {source_lines[lineno - starting_line_no].rstrip()}"
            #     vars = ", ".join(f"{name} = {vars[name]}" for name in vars)
            #     print(f"{loc:80} ({vars})")
        return DwaveReverse.traceit

