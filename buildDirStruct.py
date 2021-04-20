import sys, os
#from lxml import etree

def appendPath(path, name) :
    return(os.path.join(path,name))

class gdml_lxml() :
   def __init__(self, filename) :
      #try:
      #   from lxml import etree
      #   print('Running with lxml.etree\n')
      #   print(filename)
      #   parser = etree.XMLParser(resolve_entities=True)
      #   self.root = etree.parse(filename, parser=parser)

      #except ImportError :
      try :
             import xml.etree.ElementTree as etree
             print("Rnning with etree.ElementTree (import limitations)\n")
             self.tree = etree.parse(filename)
             print(self.tree)
             self.root = self.tree.getroot()
      except :
             print('No lxml or xml')

      print(self.root)
      self.define    = self.root.find('define')
      self.materials = self.root.find('materials')
      self.solids    = self.root.find('solids')
      self.structure = self.root.find('structure')

   def getPosition(self,posName) :
       return self.define.find(f"position[@name='{posName}']")

   def getRotation(self,rotName) :
       return self.define.find(f"rotation[@name='{rotName}']")

   def getSolid(self, sname) :
       import hashlib
       #sname = 'PUstationUnion'
       print('Get Solid : '+sname)
       print('root : '+str(hash(self.root)))
       #self.solids    = self.root.find('solids')
       print(self.solids)
       print('solids : '+str(hash(self.solids)))
       #result = hashlib.md5(bytes(self.solids))
       #print(result.hexdigest())
       #print(etree.tostring(self.solids))
       solid = self.solids.find(f'*[@name="{sname}"]')
       #if solid is not None :
       #   print(etree.tostring(solid))
       #else :
       #   print(etree.tostring(self.solids))
       #   print(str(solid))
       return(solid)

   def getMaterials(self) :
       return(self.materials)

   def getVolAsm(self, vaname) :
       return self.structure.find(f"*[@name='{vaname}']")

   def addElement(self, elemName) :
       self.docString += '<!ENTITY '+elemName+' SYSTEM "'+elemName+'">\n'
       self.gdml.append(etree.Entity(elemName))

   def closeElements(self) :
       self.docString += ']\n'

   def writeGDML(self, path, vname) :
       #indent(iself.gdml)
       etree.ElementTree(self.gdml).write(os.path.join(path,vname+'.gdml'), \
               doctype=self.docString.encode('UTF-8'))

   def dumpElement(self, elem, path) :
       es = etree.tostring(elem)
       fp = open(path,'w')
       fp.write(str(es))
   
   def writeElement(self, elem, path) :
       etree.ElementTree(elem).write(path, \
                    doctype=self.docString.encode('UTF-8'))
 
class VolAsm() :

   def __init__(self, vaname) :
       #from lxml import etree
       from xml import etree

       self.vaname    = vaname
       NS = 'http://www.w3.org/2001/XMLSchema-instance'
       location_attribute = '{%s}noNameSpaceSchemaLocation' % NS
       self.gdml = etree.Element('gdml',attrib={location_attribute: \
      'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd'})
       self.newDefine = etree.SubElement(self.gdml,'define')
       self.newSolids = etree.SubElement(self.gdml,'solids')
       self.newStruct = etree.SubElement(self.gdml,'structure')
       # Volume may have a number of physvols in different positions 
       self.volStack   = [] 
       self.posStack   = []
       self.rotStack   = []
       self.solidStack = []

   def printStackInfo(self, vaname) :
       print('Length of VolAsm Stack   in : '+vaname+' : ' \
               +str(len(self.volStack)))
       print(self.volStack)
       print('Length of Solid Stack    in : '+vaname+' : ' \
               +str(len(self.solidStack)))
       print(self.solidStack)
       print('Length of Position Stack in : '+vaname+' : ' \
               +str(len(self.posStack)))
       #print(self.getSet(self.posStack))
       print('Length of Rotation Stack in : '+vaname+' : ' \
               +str(len(self.rotStack)))
       #print(self.getSet(self.rotStack))

   def addDefine(self, d) :
       if d is not None  :
          self.newDefine.append(d)
       else :
          print('==== Problem with define')
          exit(1)
 
   def getSet(self, iList) :
       # remove duplicates from list
       return(list(set(iList)))
 
   def processPositionsStack(self, lxml) :
       posSet = self.getSet(self.posStack)
       print('Process Positions Stack : len - '+str(len(posSet)))
       for posName in posSet :
           pos = lxml.getPosition(posName)
           if pos is not None :
              self.newDefine.append(pos)
           else :
              print('Position : '+posName+' Not Found')
              exit(1)

   def processRotationsStack(self, lxml) :
       rotSet =  self.getSet(self.rotStack)
       print('Process Rotations Stack : len - '+str(len(rotSet)))
       for rotName in rotSet :
           rot = lxml.getRotation(rotName)
           if rot is not None :
              self.newDefine.append(rot)
           else :
              print('Rotation : '+rotName+' Not Found')
              exit(1)
 
   def processSolidsStack(self, lxml) :
       solidSet = self.getSet(self.solidStack)
       print('Process Solids : len - '+str(len(solidSet)))
       print(self.solidStack)
       lxml.dumpElement(lxml.solids,'/tmp/solids3')
       for sname in solidSet :
          print(sname)
          print('Len : '+str(len(sname)))
          sol = lxml.getSolid(sname)
          #sol1 = lxml.getSolid(sname)
          #if sol1 is None :
          #   print('second call failed')
          #else :
          #   print('second call Okay')
          if sol is not None :
             print(sol)
             self.newSolids.append(sol)
             lxml.dumpElement(lxml.solids,'/tmp/solids1')
          else :
             print('Solid : '+sname+' Not Found')
             lxml.dumpElement(lxml.solids,'/tmp/solids2')
             #lxml.writeElement(lxml.solids,'/tmp/solids2')
             exit(1)
   
   def processVolAsmStack(self, lxml, vaname) :
       volasmSet = self.getSet(self.volStack)
       print('Process VolAsm Set : '+str(len(volasmSet)))
       print(volasmSet)
       for vaname in volasmSet :
           volasm = lxml.getVolAsm(vaname)
           self.newStruct.append(volasm)
       if len(self.newStruct) > 0 :
          writeElement(path, vaname, 'structure', self.newStruct)

   def processPhysVols(self, lxml, volasm, path) :
       vaname = volasm.attrib.get('name')
       print('Process Phys Vols of : '+vaname)
       print(self.solidStack)
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
           print('Processing sub volume : '+pname)
           path = appendPath(path, pname)
           print('Path : '+path)
           checkDirectory(path)
           subvol = VolAsm(pname)
           print(self.solidStack)
           nv, ns, np, nr = subvol.processVolAsm(lxml,path, pname)
           print('Return from sub Volume')
           print(nv)
           print(ns)
           self.volStack   += nv
           self.solidStack += ns
           self.posStack   += np
           self.rotStack   += nr 
       print('Return process Physvols : '+vaname)
       return self.volStack, self.solidStack, self.posStack, self.rotStack
  
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

   def processVolAsm(self, lxml, path, vaname) :
       print('Processing VolAsm : '+vaname)
       volasm = lxml.getVolAsm(vaname)
       if volasm is not None :
          print(self.solidStack)
          nv, ns, np, nr = self.processPhysVols(lxml, volasm, path)
          #print(self.solidStack)
          #print(ns)
          #self.volStack   += nv
          #self.solidStack += ns
          #self.posStack   += np
          #self.rotStack   += nr 
          #print(self.solidStack)
          if volasm.tag == 'volume' : 
             solid = volasm.find('solidref')
             sname = solid.attrib.get('ref')
             self.solidStack.append(sname)
             print('Stack : '+sname)
          # Okay Now process Stacks
          print('process stacks : '+vaname)
          if len(self.volStack) > 0 :
             self.processVolAsmStack(lxml, vaname)
          if len(self.solidStack) > 0 :
             self.processSolidsStack(lxml)
          if len(self.posStack) > 0 :
             self.processPositionsStack(lxml)
          if len(self.rotStack) > 0 :
             self.processRotationsStack(lxml)
          # Write out defines
          if len(self.newDefine ) > 0 :
             writeElement(path, vaname, 'defines', self.newDefine)

       #print(str(volasm))
       #if volasm is not None :
       #   writeElement(path, vaname, 'struct', volasm)
       #   if volasm.tag == 'volume' :
       #      ns, np, nr = self.processVolume(lxml, path, volasm)
       #   elif volasm.tag == 'assembly' :
       #      ns, np, nr = self.processAssembly(lxml, path, volasm)
       #   else :
       #      print('Not Volume or Assembly : '+volasm.tag)
       #      exit(3)

       #   if ns is not None :
       #      print('Deal with solids')
       #      print(ns)
       #      #self.solidStack += ns
       #      self.processSolids(lxml)

       #   if np is not None :
       #      print('Deal with Positions')
       #      print(np)
       #      #self.posStack += np
       #      self.processPositions(lxml)

       #   if nr is not None :
       #      print('Deal with Rotations')
       #      print(nr)
       #      #self.rotStack += nr
       #      self.processRotations(lxml)

       #      writeElement(path, vaname, 'solids', self.newSolids)
          print('Return process VolAsm : '+vaname)   
          self.printStackInfo(vaname)
          return self.volStack, self.solidStack, self.posStack, self.rotStack
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
