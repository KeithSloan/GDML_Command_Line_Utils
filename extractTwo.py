import sys, os
from lxml import etree 

def checkDirectory(path) :
    if not os.path.exists(path):
       print('Creating Directory : '+path)
       os.mkdir(path)

class gdmlStacks :
   def __init__(self, iName) :
       self.gdml = etree.Element('gdml')
       self.docString = '\n<!DOCTYPE gdml [\n'
       self.tree = etree.parse(iName)
       self.root = self.tree.getroot()
       self.structure = self.tree.find('structure')
       self.oldSolids = self.tree.find('solids')
       #print(etree.fromstring(structure))
       self.newDefine = etree.Element('define')
       self.materials = self.tree.find('materials')
       self.newSolids = etree.Element('solids')
       self.newStructure = etree.Element('structure')
       self.oldDefine = self.tree.find('define') 
       #oldSolids = self.tree.find('solids')
       self.oldVols   = self.tree.find('structure')
       self.solidList = []
       self.positionList = []
       self.rotationList = []
       self.volList = []

   def processSolid(self, sname) :
       # Passed solid name volume, booleans
       solid = self.oldSolids.find(f"*[@name='{sname}']")
       print('Adding : '+sname)
       print(solid.attrib)
       if sname not in self.solidList : self.solidList.append(sname)
       if solid.tag == 'subtraction' or solid.tag == 'union' or \
          solid.tag == 'intersection' :
          print('Found Boolean')
          first = solid.find('first')
          print('first : '+str(first.attrib))
          fname = first.attrib.get('ref')
          processSolid(fname)
          second = solid.find('second')
          print('second : '+str(second.attrib))
          sname = second.attrib.get('ref')
          processSolid(sname)

   def processPhysVol(self, volasm, vname):
       pvs = volasm.findall('physvol')
       lpvs = len(pvs)
       splitSize = 75
       if lpvs < splitSize :
          for pv in pvs :
              volref = pv.find('volumeref')
              pname = volref.attrib.get('ref')
              print('physvol : '+pname)
              processVolAsm(pname)
              posref = pv.find('positionref')
              if posref is not None :
                 posname = posref.attrib.get('ref')
                 print('Position ref : '+posname)
              if posname not in positionList : 
                 positionList.append(posname)
                 rotref = pv.find('rotationref')
              if rotref is not None :
                 rotname = rotref.attrib.get('ref')
                 print('Rotation ref : '+rotname)
              if rotname not in rotationList : rotationList.append(rotname)
       else :
           oName = sys.argv[4]
           checkDirectory(oName)
           print('Split PhysVols : '+str(lpvs))
           splitCount = int(lpvs / splitSize)
           print(splitCount)
           print('SolidList : ')
           print(self.solidList)
           for r in range(splitCount) :
               newvol = vname+'_subvol'+str(r).zfill(3)
               oDir = os.path.join(oName,newvol)
               checkDirectory(oDir)
               #exportSolids(oldSolids,solidList,os.path.join(oDir,vname))
               fp = open(os.path.join(oDir, newvol+'_structure'),'wb')
               print('Range start ; '+str(r))
               start = r * splitSize
               for i in range(start, start+splitSize) :
                   fp.write(etree.tostring(pvs[i]))
               fp.close()

           splitRes = lpvs % splitSize
           print(splitRes)
           if splitRes > 0 :
              newvol = vname+'_subvol'+str(r+1).zfill(3)
              oDir = os.path.join(oName,newvol)
              checkDirectory(oDir)
              fp = open(os.path.join(oDir, newvol+'_structure'),'wb')
              start = splitCount * splitSize 
              for i in range(start, start+splitRes) :
                  fp.write(etree.tostring(pvs[i]))
              fp.close()

   def processVol(self, vol) :
       print(vol)
       print(vol.attrib)
       # Need to process physvols first
       vname = vol.attrib.get('name')
       print('volume : ' + vname)
       self.processPhysVol(vol, vname)
       if vname not in self.volList : self.volList.append(vname)
       solid = vol.find('solidref')
       sname = solid.attrib.get('ref')
       self.processSolid(sname)
       material = vol.find('materialref')
       if material is not None :
          #print('material : '+str(material.attrib))
          print('material : ' + material.attrib.get('ref'))

   def processAssembly(self, assem) :
       aname = assem.attrib.get('name')
       print('Process Assembly ; '+aname)
       processPhysVol(assem, aname)
       if aname not in volList : volList.append(aname)

   def processVolAsm(self, vaname) :
       volasm = self.structure.find(f"*[@name='{vaname}']")
       if volasm.tag == 'volume' :
          self.processVol(volasm)
       elif volasm.tag == 'assembly' :
          self.processAssembly(volasm)
       else :
          print('Not Volume or Assembly : '+volasm.tag)

   def process(self) :
       # Following works
       #vol = structure.find('volume[@name="World"]')
       # Test if Volume
       vol = self.structure.find(f"volume[@name='{volume}']")
       if vol is not None :
          self.processVol(vol)
       else : 
          # Test if Assembly
          vol = structure.find(f"assembly[@name='{volume}']")
          if vol is not None :
             self.processAssembly(vol)
          else :
             print(volume+' :  Not found as Volume or Assembly')
             exit(0)

   def processLists(self) :
       for posName in self.positionList :
           p = oldDefine.find(f"position[@name='{posName}']")
           newDefine.append(p)
       for rotName in  self.rotationList :
           p = oldDefine.find(f"rotation[@name='{rotName}']")
           newDefine.append(p)
       for solidName in self.solidList :
           print('Solid : '+solidName)
           s = self.oldSolids.find(f"*[@name='{solidName}']")
           #print(s.attrib)
           self.newSolids.append(s)
       for vaName in self.volList :
           v = self.oldVols.find(f"*[@name='{vaName}']")
           self.newStructure.append(v)

   def printLists(self) :
       print('Vol List')
       print(self.volList)
       print('Solid List')
       print(self.solidList)
       print('Position List')
       print(self.positionList)
       print('Rotation List')
       print(self.rotationList)

   def exportElement(self, dirPath, elemName, elem) :
       etree.ElementTree(elem).write(os.path.join(dirPath,elemName))
       self.docString += '<!ENTITY '+elemName+' SYSTEM "'+elemName+'">\n'
       self.gdml.append(etree.Entity(elemName))

   def exportGDML(self, oName, volume) :
       self.setup = etree.Element('setup', {'name':'Default', 'version':'1.0'})
       etree.SubElement(self.setup,'world', { 'ref' : self.volList[-1]})
       print("Write GDML structure to Directory")
       NS = 'http://www.w3.org/2001/XMLSchema-instance'
       location_attribute = '{%s}noNameSpaceSchemaLocation' % NS
       gdml = etree.Element('gdml',attrib={location_attribute: \
            'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd'})

       self.docString = '\n<!DOCTYPE gdml [\n'
       checkDirectory(oName)
       #self.exportElement(oName, 'constants',constants)
       self.exportElement(oName, volume+'_define',self.newDefine)
       self.exportElement(oName, volume+'_materials',self.materials)
       self.exportElement(oName, volume+'_solids',self.newSolids)
       self.exportElement(oName, volume+'_structure',self.newStructure)
       self.exportElement(oName, volume+'_setup',self.setup)
       self.docString += ']>\n'
       #indent(gdml)
       etree.ElementTree(gdml).write(os.path.join(oName,volume+'.gdml'), \
               doctype=self.docString.encode('UTF-8'))

if len(sys.argv)<5:
  print ("Usage: sys.argv[0] <parms> <Volume> <in_file> <Out_directory> <materials>")
  print("/n For parms the following are or'ed together")
  print(" For future")
  sys.exit(1)

parms  = int(sys.argv[1])
volume = sys.argv[2]
iName = sys.argv[3]
oName = sys.argv[4]

print('\nExtracting Volume : '+volume+' from : '+iName+' to '+oName)
gs = gdmlStacks(iName)
gs.process()
gs.processLists()
gs.printLists()
gs.exportGDML(oName,volume)
