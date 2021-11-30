'''
Created on 30 nov 2021

@author: Alarcos
'''

from xml.etree import ElementTree as ET
from io import BytesIO
import os

class KDMGenerator(object):
    
    KDM_FOLDER = ("./kdm") 
    
    def __init__(self):
        '''
        Constructor
        '''


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

        #segment = ET.Element("Segment")
        codeModel = ET.SubElement(segment, "model", {'xmi:id':'id.0', 'xmi:type':'code:CodeModel'})
        
        codeAsembly = ET.SubElement(codeModel, "codeElement", {'xmi:id':'id.1', 'xmi:type':'code:CodeAsembly'})
        
        callableUnit = ET.SubElement(codeAsembly, "codeElement", {'xmi:id':'id.2', 'xmi:type':'code:CallableUnit', 'kind':'regular', 'name':'DWAVE_FUNCTION'})
        
        ET.SubElement(callableUnit, "entryFlow", {'xmi:id':'id.3', 'to':'id.4', 'from':'id.2'})
        
        actionElement = ET.SubElement(callableUnit, "codeElement", {'xmi:id':'id.4', 'xmi:type':'action:ActionElement', 'kind':'compound', 'name':'H'}) 
        
        ET.SubElement(actionElement, "source", {'xmi:id':'id.5', 'snippet':str(H)})


        KDMGenerator().indent(segment)

        tree = ET.ElementTree(segment)
        
        print(segment)
        
        tree.write(fileName, encoding='utf-8', xml_declaration=True)
        
        
        
def main():
    KDMGenerator().generateKDM('H=1*b+1*k+2*a*c-2*a*k-2*b*c0', 'test')
    

main()