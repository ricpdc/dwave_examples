'''
Created on 30 nov 2021

@author: Alarcos
'''

from xml.etree import ElementTree as ET
from lxml import etree
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
        self.elementsMap = {}
        
    def getElementId(self, element):
        return self.elementsMap[element]
    
    def getElementByName(self, name):
        
        for key in self.elementsMap:
            if 'name' in key.attrib.keys() and key.attrib['name'] == name:
                return key
        return None

    
    def prettyPrintXml(self, xmlFilePathToPrettyPrint):
        assert xmlFilePathToPrettyPrint is not None
        parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
        document = etree.parse(xmlFilePathToPrettyPrint, parser)
        document.write(xmlFilePathToPrettyPrint, pretty_print=True, encoding='utf-8')
    
    
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
        
        
        accumulatedSum = ''
        partialSum = None
        totalSum = None
        
        
        sums = re.split(r'\+|-',  exp)
        for s in sums:  
            
            if exp.find(s) == 0:
                operator='+'
            else:
                operator = exp[exp.find(s)-1:exp.find(s)]
            #print('\t' + operator)

            eId=self.getId();
            actionElementMultiply = ET.SubElement(actionElement, "codeElement", {'xmi:id':eId, 'xmi:type':'action:ActionElement', 'kind':'Multiply', 'name':str(s)})
            self.elementsMap[actionElementMultiply] = eId

            
            terms = s.split('*')
            for t in terms:
                #print('\t\t'+t)
                
                term = self.getElementByName(str(t))
                
                if term is None:
                    eId=self.getId();
                    term = ET.SubElement(actionElement, "codeElement", {'xmi:id':eId, 'xmi:type':('code:Value' if terms.index(t) == 0 else 'code:StorableUnit'), 'name':str(t)})
                    self.elementsMap[term] = eId

                eId=self.getId();
                reads = ET.SubElement(actionElementMultiply, "codeElement", {'xmi:id':eId, 'xmi:type':'action:Reads', 'from': self.getElementId(actionElementMultiply), 'to':self.getElementId(term)})
                self.elementsMap[reads] = eId
            
            
            eId=self.getId();
            storableUnitMult = ET.SubElement(actionElement, "codeElement", {'xmi:id':eId, 'xmi:type':'code:StorableUnit', 'kind':'register', 'name':'multiply_'+str(s)})
            self.elementsMap[storableUnitMult] = eId
            partialSum = storableUnitMult
            
            eId=self.getId();
            writes = ET.SubElement(actionElementMultiply, "codeElement", {'xmi:id':eId, 'xmi:type':'action:Writes', 'from': self.getElementId(actionElementMultiply), 'to':self.getElementId(storableUnitMult)})
            self.elementsMap[writes] = eId   
            
            accumulatedSum += operator + str(s)
            
            if sums.index(s) == 0:
                totalSum = partialSum
                continue

            
            eId=self.getId();
            actionElementSum = ET.SubElement(actionElement, "codeElement", {'xmi:id':eId, 'xmi:type':'action:ActionElement', 'kind':('Add' if operator == '+' else 'Subtract'), 'name':accumulatedSum})
            self.elementsMap[actionElementSum] = eId
            
            eId=self.getId();
            readsSum1 = ET.SubElement(actionElementSum, "codeElement", {'xmi:id':eId, 'xmi:type':'action:Reads', 'from': self.getElementId(actionElementSum), 'to':self.getElementId(totalSum)})
            self.elementsMap[readsSum1] = eId
            
            eId=self.getId();
            readsSum2 = ET.SubElement(actionElementSum, "codeElement", {'xmi:id':eId, 'xmi:type':'action:Reads', 'from': self.getElementId(actionElementSum), 'to':self.getElementId(partialSum)})
            self.elementsMap[readsSum2] = eId
            
            eId=self.getId();
            storableUnitSum = ET.SubElement(actionElement, "codeElement", {'xmi:id':eId, 'xmi:type':'code:StorableUnit', 'kind':'register', 'name':'accumulated_'+accumulatedSum})
            self.elementsMap[storableUnitSum] = eId
            totalSum = storableUnitSum
            
            eId=self.getId();
            writesSum = ET.SubElement(actionElementSum, "codeElement", {'xmi:id':eId, 'xmi:type':'action:Writes', 'from': self.getElementId(actionElementSum), 'to':self.getElementId(storableUnitSum)})
            self.elementsMap[writesSum] = eId 
                

        tree = ET.ElementTree(segment)
        
        tree.write(fileName, encoding='utf-8', xml_declaration=True)
        
        self.prettyPrintXml(fileName)
        
        
        
        
# def main():
#     KDMGenerator().generateKDM('H=1*b+1*k+2*a*c-2*a*k-2*b*c', 'test')
#
#
# main()