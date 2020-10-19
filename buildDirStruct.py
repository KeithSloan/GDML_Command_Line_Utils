import sys, os
from lxml import etree 

def checkDirectory(path) :
    if not os.path.exists(path):
       print('Creating Directory : '+path)
       os.mkdir(path)

def writeElement(path, sname, type, elem) :
    import os
    #global gdml, docString

    fpath = os.path.join(path,sname+'_'+type)
    print('writing file : '+fpath)
    etree.ElementTree(elem).write(fpath)
    #docString += '<!ENTITY '+elemName+' SYSTEM "'+elemName+'">\n'
    #gdml.append(etree.Entity(elemName))

def processSolid(path, sname) :
   # Passed solid name volume, booleans
   global solidList, solids
   solid = solids.find(f"*[@name='{sname}']")
   print('Adding : '+sname)
   print(solid.attrib)
   if path is not None :
      writeElement(path, sname, 'solid', solid)

def processPhysVol(path, vaname, volasm):
   positionList = []
   rotationList = []
   for pv in volasm.findall('physvol') :
      volref = pv.find('volumeref')
      pname = volref.attrib.get('ref')
      print('physvol : '+pname)
      npath = os.path.join(path,pname)
      print('New path : '+npath)
      checkDirectory(npath)
      processVolAsm(npath, pname)
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
   newDefine = etree.SubElement(gdml,'define')
   for posName in positionList :
       p = defines.find(f"position[@name='{posName}']")
       newDefine.append(p)
   for rotName in rotationList :
       p = defines.find(f"rotation[@name='{rotName}']")
       newDefine.append(p)
   writeElement(path, vaname, 'defines', newDefine)

def processVol(path, vol) :
   global volList, solidList, oldSolids
   print(vol)
   print(vol.attrib)
   # Need to process physvols first
   vname = vol.attrib.get('name')
   print('volume : ' + vname)
   processPhysVol(path, vname, vol)
   solid = vol.find('solidref')
   sname = solid.attrib.get('ref')
   processSolid(path, sname)
   material = vol.find('materialref')
   if material is not None :
      #print('material : '+str(material.attrib))
      print('material : ' + material.attrib.get('ref'))

def processAssembly(path, assem) :
    aname = assem.attrib.get('name')
    print('Process Assembly ; '+aname)
    processPhysVol(path, aname, assem)

def processVolAsm(path, vaname) :
    volasm = structure.find(f"*[@name='{vaname}']")
    writeElement(path, vaname, 'struct', volasm)
    if volasm.tag == 'volume' :
       processVol(path, volasm)
    elif volasm.tag == 'assembly' :
       processAssembly(path, volasm)
    else :
       print('Not Volume or Assembly : '+volasm.tag)

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
gdml = etree.Element('gdml')

volume = sys.argv[2]
iName = sys.argv[3]
oName = sys.argv[4]

print('\nExtracting Volume : '+volume+' from : '+iName+' to '+oName)
checkDirectory(oName)
path = os.path.join(oName,volume)
checkDirectory(path)
tree = etree.parse(iName)
root = tree.getroot()
structure = tree.find('structure')
solids = tree.find('solids')
defines = tree.find('define')
#print(etree.fromstring(structure))
processVolAsm(path, volume)
#setup = etree.Element('setup', {'name':'Default', 'version':'1.0'})
#etree.SubElement(setup,'world', { 'ref' : volList[-1]})

print("Write GDML structure to Directory")
NS = 'http://www.w3.org/2001/XMLSchema-instance'
location_attribute = '{%s}noNameSpaceSchemaLocation' % NS
gdml = etree.Element('gdml',attrib={location_attribute: \
      'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd'})

docString = '\n<!DOCTYPE gdml [\n'
