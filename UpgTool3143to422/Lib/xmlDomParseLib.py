#!/usr/bin/python
import os
import sys
import stat
import shutil
import warnings
import re
from xml.dom.minidom import parse, parseString

warnings.filterwarnings("ignore")

class xmlFileParser:

    def __init__(self, filename, perm='w'):
        '''
        Init XML file parse instance.
        '''
        self.fileName = filename
        self.fileHandler = None
        self.docObj = None
        self.xpathCtxt = None
        self.permission = perm
        self.bak = False
        self.tagLists = []
        self.newNode = None                          
       
    def parseDomObj(self):
        '''
        Open the XML file in this instance.
        '''
        self.docObj = parse(self.fileName)
        self.xpathCtxt = self.docObj.documentElement

    def getElements(self, xpath):
        '''
        Get the elements of xml by calling method getElementsByTagName().
        '''
        nodeLists = []
        nodeLists = self.xpathCtxt.getElementsByTagName(xpath)

        return nodeLists

    def getNodeObj(self, xpath, oldID):
        '''
        Get the object of node element.
        '''
        nodeObjList = []
        elements = self.getElements(xpath)
        for element in elements:
            node = self.searchModifier(element)
            eleID = node.attributes['id'].value
            if eleID == oldID:
                nodeObjList.append(node)

        return list(set(nodeObjList))

    def replaceNodeValue(self, xpath):
        '''
        Execute the parsing process with xpath expression.
        '''
        # Get all nodes (node list) for this xpath.
        dstNodes = []
        dstNodes = self.getElements(xpath)
       
        if len(dstNodes) == 0:
            return
        else:
            self.bakXmlFiles()
            for dstNode in dstNodes:
                content = dstNode.childNodes[0].nodeValue
                if (content == "SPONT_ON_OVERLOAD"):
                    dstNode.childNodes[0].replaceData(0, 17, "LOG_ON_OVERLOAD")
   
    def cloneNodes(self, oldNode):
        '''
        Copy the node and append to the end of above node.
        '''
        # Clone a new node
        self.newNode = oldNode.cloneNode(True)

        # Append the new node to the end of the old one
        oldNode.parentNode.appendChild(self.newNode)
        
        # Back up the modified xml file
        self.bakXmlFiles()

    def getPeersTagName(self, node):
        '''
        Get all tagNames of peers which have no sub-nodes.
        '''
        hasElementNode = False

        for tag in node.childNodes:
            if tag.nodeType == tag.ELEMENT_NODE:
                for childTag in tag.childNodes:
                    if childTag.nodeType == childTag.ELEMENT_NODE:
                        hasElementNode = True
                        break
                if hasElementNode == True:
                    self.getPeersTagName(tag)
                    hasElementNode = False
                else:                
                    self.tagLists.append(tag)
        return self.tagLists

    def getNodeAttrValue(self, prefix, attr, attrName1, attrName2):
        '''
        Get the attributes' values of nodes.
        '''
        resultTuple = ()
        resultID = ''
        resultModifier =''
        nodes = []
        xpath = prefix + ":" + attr
        nodes = self.getElements(xpath)
        if nodes != []:
            n = nodes[0]
            if n.hasAttributes() == False:
                n = self.searchModifier(n)   
                
            resultID = n.attributes[attrName1].value
            resultModifier = n.attributes[attrName2].value
            resultTuple = (n, resultID, resultModifier)
        return resultTuple

    def searchModifier(self,node):
        '''
        Search the modifier attribute
        '''
        if u'modifier' in node.attributes.keys():
            return node
        else:
            # Recursion
            return self.searchModifier(node.parentNode)

    def updateNodeAttrValue(self, node, modifier):
        '''
        Update the attributes' values of nodes.
        '''
        node.setAttribute('modifier', modifier)

    def deleteNode(self, prefix, attr):
        '''
        Delete the node which has read-only or error attributes.
        '''
        # Define the format of xpath
        xpath = prefix + ":" + attr
        # Get all nodes (node list) for this xpath.
        dstNodes = self.getElements(xpath)
        if len(dstNodes) != 0:
            self.bakXmlFiles()

        for dstNode in dstNodes:
            # Get attribute's parent node
            attrParent=dstNode.parentNode
            counter = 0
            childNodes = attrParent.childNodes
            for child in childNodes:
                if child.nodeType == dstNode.nodeType:
                    counter += 1

            if counter > 1:
                # Delete dstNode
                attrParent.removeChild(dstNode)
            else:
                # Delete parent node
                attrParent.parentNode.removeChild(attrParent)
    
    def delDuplicatedNode(self, dstNodesEle):
        '''
        Delete one of the duplicated attributes in one xml file.
        '''
        # Get attribute's parent node
        attrParent=dstNodesEle.parentNode
        counter = 0
        childNodes = attrParent.childNodes
        for child in childNodes:
            if child.nodeType == dstNodesEle.nodeType:
                counter += 1
        if counter > 1:
            # Delete dstNode
            attrParent.removeChild(dstNodesEle)
        else:
            # Delete parent node
            attrParent.parentNode.removeChild(attrParent)

    def bakXmlFiles(self):
        # Create backup of this XML file
        backupName = self.fileName + ".bak"
        if not os.path.exists(backupName):
            shutil.copy(self.fileName, backupName)
        self.bak = True

    def cleanUpProc(self):
        '''
        Save the file that was modified, and free objects.
        '''
        # Open output file
        self.fileHandler = open(self.fileName, self.permission)

        # delete blank lines
        noBlankPrint = lambda f: '\n'.join([line for line in f.toprettyxml(' ' * 4, encoding='UTF-8').split('\n') if line.strip()]) 
        text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
        prettyXml = text_re.sub('>\g<1></', noBlankPrint(self.docObj))
        
        # write to this file
        self.fileHandler.write(prettyXml)

        #self.docObj = parseString(prettyXml)
        #self.docObj.writexml(self.fileHandler, encoding = 'UTF-8')

        # clear dom object
        self.docObj.unlink()

        # close file
        self.fileHandler.close()

def getXmlFileList(dir):
    '''
    Get all xml files from the directory and its' sub directory.
    '''
    fileList = []
    # Only to handle the files naming begin with 'xml' and end with 'xml'
    pat = re.compile('^xml.*xml$')

    for (parents, dirnames, files) in os.walk(dir, topdown = True):
        for file in files:
            if pat.match(file) != None:
                fileName = os.path.join(parents, file)
                fileList.append(fileName)
    return fileList
    
def chgBakToXml(dir):
    '''
    Change the file whose postfix is .bak to standard xml format.
    '''
    xmlList = os.listdir(dir)
    for fileName in xmlList:
        if '.bak' in fileName:
            absName = os.path.join(dir, fileName)
            bakAttr = xmlFileParser(absName, 'w')
            bakAttr.parseDomObj()
            bakAttr.cleanUpProc()
