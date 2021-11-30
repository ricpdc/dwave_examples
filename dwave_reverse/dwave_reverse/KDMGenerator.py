'''
Created on 30 nov 2021

@author: Alarcos
'''

from xml.etree import ElementTree as ET
import os
import re

class KDMGenerator(object):
    
    KDM_FOLDER = ("./kdm") 
    
    id = 0
    elementsMap = {}
    
    def __init__(self):
        '''
        Constructor
        '''


    def getId(self):
        KDMGenerator.id += 1
        return 'id.'+str(KDMGenerator.id)
    
    def resetId(self):
        KDMGenerator.id = 0
        elementsMap = {}
        
    def getElementId(self, element):
        return self.elementsMap[element]
        


    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        j = "\n" + (level-1)*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                KDMGenerator().indent(subelem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem
    
    
    def generateKDM(self, H, name):
        print (H)
        
        self.resetId()
        
        if not os.path.isdir(KDMGenerator.KDM_FOLDER):
            os.makedirs(KDMGenerator.KDM_FOLDER)
         
        fileName = KDMGenerator.KDM_FOLDER+"/"+name+".kdm"
        
        
        ns = {
            'xmi': 'http://www.omg.org/spec/XMI/20110701',
            'action': 'http://www.omg.org/spec/KDM/20160201/action',
            'code': 'http://www.omg.org/spec/KDM/20160201/code',
            
        }
        for prefix, uri in ns.items():
            ET.register_namespace(prefix, uri)
        ET.register_namespace('kdm', 'http://www.omg.org/spec/KDM/20160201/kdm')
        
        segment = ET.fromstring('<kdm:Segment xmlns:kdm="http://www.omg.org/spec/KDM/20160201/kdm"></kdm:Segment>')
        

        segment.set('name', name)
        for prefix, uri in ns.items():
            segment.set('xmlns:'+prefix, uri)

        eId=self.getId();
        codeModel = ET.SubElement(segment, "model", {'xmi:id':eId, 'xmi:type':'code:CodeModel'})
        self.elementsMap[codeModel] = eId
        
        eId=self.getId();
        codeAsembly = ET.SubElement(codeModel, "codeElement", {'xmi:id':'id.'+eId, 'xmi:type':'code:CodeAsembly'})
        self.elementsMap[codeAsembly] = eId
        
        eId=self.getId();
        callableUnit = ET.SubElement(codeAsembly, "codeElement", {'xmi:id':eId, 'xmi:type':'code:CallableUnit', 'kind':'regular', 'name':'DWAVE_FUNCTION'})
        self.elementsMap[callableUnit] = eId
        
        eId=self.getId();
        entryFlow = ET.SubElement(callableUnit, "entryFlow", {'xmi:id':eId, 'from':eId})
        self.elementsMap[entryFlow] = eId
        
        eId=self.getId();
        actionElement = ET.SubElement(callableUnit, "codeElement", {'xmi:id':eId, 'xmi:type':'action:ActionElement', 'kind':'compound', 'name':'H'}) 
        self.elementsMap[actionElement] = eId
        
        entryFlow.set('to', self.getElementId(actionElement))
        
        eId=self.getId();
        source = ET.SubElement(actionElement, "source", {'xmi:id':eId, 'snippet':str(H)})
        self.elementsMap[source] = eId
        
        
        h = str(H.split("=")[0])
        print(h)
        exp = str(H.split("=")[1])
        
        sums = re.split(r'\+|-',  exp)
        for s in sums:            
            if exp.find(s) == 0:
                operator='+'
            else:
                operator = exp[exp.find(s)-1:exp.find(s)]
            print('\t' + operator)
            
            terms = s.split('*')
            for t in terms:
                print('\t\t'+t)


        KDMGenerator().indent(segment)

        tree = ET.ElementTree(segment)
        
        print(segment)
        
        tree.write(fileName, encoding='utf-8', xml_declaration=True)
        
        
        
def main():
    KDMGenerator().generateKDM('H=1*b+1*k+2*a*c-2*a*k-2*b*c', 'test')
    

main()