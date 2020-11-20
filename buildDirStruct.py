import sys, os
from lxml import etree

class gdml_lxml() :
   def __init__(self, filename) :
      try:
         from lxml import etree
         print('Running with lxml.etree\n')
         print(filename)
         parser = etree.XMLParser(resolve_entities=True)
         self.root = etree.parse(filename, parser=parser)

      except ImportError :
         try :
             import xml.etree.ElementTree as etree
             print("Rnning with etree.ElementTree (import limitations)\n")
             self.tree = etree.parse(filename)
             self.root = self.tree.getroot()
         except :
             print('No lxml or xml')

      self.define    = self.root.find('define')
      self.materials = self.root.find('materials')
      self.solids    = self.root.find('solids')
      self.structure = self.root.find('structure')

   def getPosition(self,posName) :
       return self.define.find(f"position[@name='{posName}']")

   def getRotation(self,rotName) :
       return self.define.find(f"rotation[@name='{rotName}']")

   def getSolid(self, sname) :
       return self.solids.find(f"*[@name='{sname}']")

   def getMaterials(self) :
       return(self.materials)

   def getVolAsm(self, vaname) :
       return self.structure.find(f"*[@name='{vaname}']")

   def addElement(self, elemName) :
       self.docString += '<!ENTITY '+elemName+' SYSTEM "'+elemName+'">\n'
       self.gdml.append(etree.Entity(elemName))

   def closeElements(self) :
       self.docString += ']\n'

   def writeGDML(self, path,vname) :
       #indent(iself.gdml)
       etree.ElementTree(self.gdml).write(os.path.join(path,vname+'.gdml'), \
               doctype=self.docString.encode('UTF-8'))

class VolAsm() :

   def __init__(self, vaname) :
       from lxml import etree

       self.vaname    = vaname
       NS = 'http://www.w3.org/2001/XMLSchema-instance'
       location_attribute = '{%s}noNameSpaceSchemaLocation' % NS
       self.gdml = etree.Element('gdml',attrib={location_attribute: \
      'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd'})
       self.newDefine = etree.SubElement(self.gdml,'define')
       self.newSolids = etree.SubElement(self.gdml,'solids')
       # Volume may have a number of physvols in different positions 
       self.volStack   = [] 
       self.posStack   = []
       self.rotStack   = []
       self.solidStack = []

   def addDefine(self, d) :
       if d is not None  :
          self.newDefine.append(d)
       else :
          print('==== Problem with define')
          exit(1)
 
   def getSet(self, iList) :
       # remove duplicates from list
       return(list(set(iList)))
 
   def processPositions(self, lxml) :
       for posName in self.getSet(self.posStack) :
           pos = lxml.getPosition(posName)
           if pos is not None :
              self.newDefine.append(pos)
           else :
              print('Position : '+posName+' Not Found')
              exit(1)

   def processRotations(self, lxml) :
       for rotName in self.getSet(self.rotStack) :
           rot = lxml.getRotation(rotName)
           if rot is not None :
              self.newDefine.append(rot)
           else :
              print('Rotation : '+rotName+' Not Found')
              exit(1)
 
   def processSolids(self, lxml) :
       print('Process Solids')
       print(self.solidStack)
       for sname in self.getSet(self.solidStack) :
          sol = lxml.getSolid(sname)
          if sol is not None :
             self.newSolids.append(sol)
          else :
             print('Solid : '+sname+' Not Found')
             exit(1)

   def processPhysVols(self, lxml, volasm, path) :
       vaname = volasm.attrib.get('name')
       print('Process Phys Vols of : '+vaname)
       for pv in volasm.findall('physvol') :
           volref = pv.find('volumeref')
           pname = volref.attrib.get('ref')
           print('physvol : '+pname)
           self.volStack.append(pname)
           posref = pv.find('positionref')
           if posref is not None :
              posname = posref.attrib.get('ref')
              self.posStack.append(posname)
           rotref = pv.find('rotationref')
           if rotref is not None :
              rotname = rotref.attrib.get('ref')
              self.rotStack.append(rotname)
       self.processVolAsms(lxml)
       print('Length of Position Stack in : '+vaname+' : ' \
               +str(len(self.posStack)))
       #print(self.getSet(self.posStack))
       print('Length of Rotation Stack in : '+vaname+' : ' \
               +str(len(self.rotStack)))
       #print(self.getSet(self.rotStack))
       #self.processPositions(lxml)
       #self.processRotations(lxml)
       #self.processSolids(lxml)
       #writeElement(path, vaname, 'defines', self.newDefine)
       #writeElement(path, vaname, 'solids', self.newSolids)
       #print('PhysVols : '+str(self.solidStack))
       return self.solidStack, self.posStack, self.rotStack
  
   def processVolume(self, lxml, path, vol) :
       # return solid
       print('Process Volume')
       print(vol)
       print(vol.attrib)
       # Need to process physvols first
       vname = vol.attrib.get('name')
       print('volume : ' + vname)
       ns, np, nr = self.processPhysVols(lxml, vol, path)
       self.solidStack += ns
       self.posStack += np
       self.rotStack += nr 
       solid = vol.find('solidref')
       sname = solid.attrib.get('ref')
       self.solidStack.append(sname)
       material = vol.find('materialref')
       if material is not None :
          #print('material : '+str(material.attrib))
          print('material : ' + material.attrib.get('ref'))
       materials = lxml.getMaterials()
       writeElement(path, vname, 'materials', materials)
       print('Solids in : '+vname+' : '+str(self.solidStack))
       return self.solidStack, self.posStack, self.rotStack

   def processAssembly(self, lxml, path, assem) :
       aname = assem.attrib.get('name')
       print('Process Assembly ; '+aname)
       self.processPhysVols(lxml, assem, path)
       #ns, np, nr = self.processPhysVols(lxml, assem, path)
       #self.solidStack += ns
       #self.posStack += np
       #self.rotStack += nr 
       return self.solidStack, self.posStack, self.rotStack

   def processVolAsm(self, lxml, path, vaname) :
       print('Processing VolAsm : '+vaname)
       volasm = lxml.getVolAsm(vaname)
       print(volasm)
       print(str(volasm))
       if volasm is not None :
          writeElement(path, vaname, 'struct', volasm)
          if volasm.tag == 'volume' :
             ns, np, nr = self.processVolume(lxml, path, volasm)
          elif volasm.tag == 'assembly' :
             ns, np, nr = self.processAssembly(lxml, path, volasm)
          else :
             print('Not Volume or Assembly : '+volasm.tag)
             exit(3)

          if ns is not None :
             print('Deal with solids')
             print(ns)
             #self.solidStack += ns
             self.processSolids(lxml)

          if np is not None :
             print('Deal with Positions')
             print(np)
             #self.posStack += np
             self.processPositions(lxml)

          if nr is not None :
             print('Deal with Rotations')
             print(nr)
             #self.rotStack += nr
             self.processRotations(lxml)

             writeElement(path, vaname, 'solids', self.newSolids)
             return self.solidStack, self.posStack, self.rotStack
       else :
          print(vaname+ ' : Not Found')
          exit(3)

   def processVolAsms(self, lxml) :
       print('Print process Volume/Assemblies')
       print('Length of volStack : '+str(len(self.volStack)))
       #print(self.volStack)
       volSet = self.getSet(self.volStack)
       print('Length of vol Set : '+str(len(volSet)))
       print(volSet)
       #    npath = os.path.join(path,pname)
       #    print('New path : '+npath)
       #    checkDirectory(npath)

def checkDirectory(path) :
    if not os.path.exists(path):
       print('Creating Directory : '+path)
       os.mkdir(path)

def writeElement(path, sname, type, elem) :
    import os

    fpath = os.path.join(path,sname+'_'+type)
    print('writing file : '+fpath)
    etree.ElementTree(elem).write(fpath)

def exportElement(dirPath, elemName, elem) :
    import os
    global gdml, docString

    etree.ElementTree(elem).write(os.path.join(dirPath,elemName))
    docString += '<!ENTITY '+elemName+' SYSTEM "'+elemName+'">\n'
    gdml.append(etree.Entity(elemName))

if len(sys.argv)<5:
  print ("Usage: sys.argv[0] <parms> <Volume> <in_file> <Out_directory> <materials>")
  print("/n For parms the following are or'ed together")
  print(" For future")
  sys.exit(1)

parms  = int(sys.argv[1])
vName = sys.argv[2]
iName = sys.argv[3]
oName = sys.argv[4]

print('\nExtracting Volume : '+vName+' from : '+iName+' to '+oName)
checkDirectory(oName)
path = os.path.join(oName,vName)
checkDirectory(path)
lxml = gdml_lxml(iName)
volasm = VolAsm(vName)
volasm.processVolAsm(lxml, path, vName)
#setup = etree.Element('setup', {'name':'Default', 'version':'1.0'})
#etree.SubElement(setup,'world', { 'ref' : volList[-1]})
