import os
import sys
import svgwrite

rootpath = "YOUR ARTIQ ROOT PATH\\artiq\\gateware\\"
class SvgTextLine():
    def __init__(self, height, length):
        self.idx = 0
        self.rectstartidx = 0
        self.height = height
        self.length = length


class ArtiqObjectProperties():
    def __init__(self, objectname):
        self.name = objectname
        self.inherit = []
        self.content = []
    
    def svgdrawobject(self, stl, dwg, dwgg, endofclass=False):
        stl.idx = stl.idx + 1
        dwgg.add(dwg.text(self.name, insert=(10, stl.idx*stl.height), fill=svgwrite.rgb(0, 128, 128, 'RGB')))
        for inherititems in self.inherit:
            stl.idx = stl.idx + 1
            dwgg.add(dwg.text(inherititems, insert=(10, stl.idx*stl.height), fill=svgwrite.rgb(128, 128, 128, 'RGB')))
        for contentitems in self.content:
            stl.idx = stl.idx + 1
            dwgg.add(dwg.text(contentitems, insert=(10, stl.idx*stl.height)))
        if not endofclass:
            dwgg.add(dwg.line((0, stl.idx*stl.height + 4), (stl.length, stl.idx*stl.height + 4), stroke=svgwrite.rgb(0, 0, 0, '%')))
        

class ArtiqClass():
    def __init__(self, classname, objectlist):
        self.name = classname
        self.hierarchy = objectlist
        self.inheritance = ArtiqObjectProperties("inheritance")
        self.submodules = ArtiqObjectProperties("submodules")
        self.signals = ArtiqObjectProperties("signals")
        self.clockdomains = ArtiqObjectProperties("clockdomains")
        self.objects = ArtiqObjectProperties("objects")
        self.functions = ArtiqObjectProperties("functions")
    
    def printclass(self):
        print(".".join(self.hierarchy)+"."+self.name)
        print(self.inheritance.name+": "+str(self.inheritance.content))
        print(self.submodules.name+": "+str(self.submodules.content))
        print(self.signals.name+": "+str(self.signals.content))
        print(self.clockdomains.name+": "+str(self.clockdomains.content))
        print(self.objects.name+": "+str(self.objects.content))
        print(self.functions.name+": "+str(self.functions.content))

    
def scancodesignature(stringline,lrequiredsubstring,rrequiredsubstring,lstripsubstring):
    lrequiredend = 1
    if "" != lrequiredsubstring:
        lrequiredend = stringline.find(lrequiredsubstring)
    rrequiredend = len(stringline) - 1
    if "" != rrequiredsubstring:
        rrequiredend = stringline.find(rrequiredsubstring)
    artiqname = ""
    if -1 != lrequiredend and -1 != rrequiredend:
        lstripindex = stringline.find(lstripsubstring)
        if -1 != lstripindex:
            artiqname = stringline[lstripindex + len(lstripsubstring):rrequiredend]
        else:
            artiqname = stringline[len(stringline) - len(stringline.lstrip()):rrequiredend]
    return artiqname

def filepathname2objectlist(filepathname):
    if filepathname.startswith(rootpath):
        if filepathname.endswith("\\__init__.py"):
            objectpath = filepathname[len(rootpath):-12]
        elif filepathname.endswith(".py"):
            objectpath = filepathname[len(rootpath):-3]
        else:
            return False
        return objectpath.replace("\\",".").split(".")
    else:
        return False

class ImportFileObject():
    def __init__(self, fileline):
        importfromstr = fileline[fileline.find("from artiq.gateware")+20:fileline.find(" import")].strip()
        importlibstr = fileline[fileline.find(" import")+8:].strip()
        self.objectlist = []
        if importfromstr=="":
            importfilepath = rootpath + importlibstr
        else:
            importfilepath = rootpath + importfromstr.replace(".","\\") + "\\" + importlibstr
        if os.path.isfile(importfilepath + "\\__init__.py"):
            self.objectfilepath = importfilepath + "\\__init__.py"
            self.objectlist = filepathname2objectlist(self.objectfilepath)
        elif os.path.isfile(importfilepath + ".py"):
            self.objectfilepath = importfilepath + ".py"
            self.objectlist = filepathname2objectlist(self.objectfilepath)
        else:
            importfilepath = rootpath + importfromstr.replace(".","\\")
            if os.path.isfile(importfilepath + "\\__init__.py"):
                self.objectfilepath = importfilepath + "\\__init__.py"
                self.objectlist = filepathname2objectlist(self.objectfilepath)
            elif os.path.isfile(importfilepath + ".py"):
                self.objectfilepath = importfilepath + ".py"
                self.objectlist = filepathname2objectlist(self.objectfilepath)
            

def main():
    filenamepath = sys.argv[1]
    filenamepath = filenamepath.replace("/","\\")
    print(filenamepath)
    currentobjectlist = filepathname2objectlist(filenamepath)
    if isinstance(currentobjectlist,bool):
        return None
    f = open(filenamepath,"r")
    filelines = f.readlines()
    
    classes = []
    currentclassname = ""

    artiqgatewarepath = "C:\\Users\\engs1457\\OneDrive\\Documents\\Work\\Code\\artiq_master\\artiq\\artiq\\gateware\\"
    importedobject = []
    filelinesidx = 1
    for idx, fl in enumerate(filelines, start = filelinesidx):
        if fl.startswith("from artiq.gateware"):
            importpath = fl[fl.find("from artiq.gateware")+20:fl.find(" import")]
            if fl.endswith("import *\n"):
                ifo = ImportFileObject(fl)
                existedimportedobject = False
                for ipob in importedobject:
                    if len(set(ipob) & set(ifo.objectlist)) == len(ifo.objectlist):
                        if len(set(ipob) & set(ifo.objectlist)) == len(ipob):
                            existedimportedobject = True
                if existedimportedobject:
                    continue
                importedobject.append(ifo.objectlist)
                f = open(ifo.objectfilepath,"r")
                importedfilelines = f.readlines()
                filelinesidx = idx
                for ifl in importedfilelines:
                    filelines.insert(idx,ifl)
                    idx = idx + 1
                print(currentobjectlist)
                print(ifo.objectlist)
                filelines.insert(idx,"endofobject "+".".join(ifo.objectlist)+"\n")
                idx = idx + 1
                filelines.insert(idx,"startofobject "+".".join(currentobjectlist)+"\n")
                idx = idx + 1
                currentobjectlist = ifo.objectlist
                print("Found import * \n")
                continue
            elif fl.find("(") and fl.endswith(",\n"):
                while 1:
                    fl = fl.replace("\n"," ")
                    fl = fl + filelines[idx].strip()
                    idx = idx + 1
                    if filelines[idx - 1].endswith(")\n"):
                        objtoimport = fl[fl.find("(")+1:fl.find(")")].split(",")
                        importedfilelines = []
                        for objti in objtoimport:
                            importedfilelines.append("from artiq.gateware."+importpath+" import "+ objti.strip() + "\n")
                        break
                filelinesidx = idx
                for ifl in importedfilelines:
                    filelines.insert(idx,ifl)
                    idx = idx + 1
                print("Found import multi-lines \n")
                continue
            elif -1 != fl[fl.find(" import")+8:].find(", "):
                objtoimport = fl[fl.find(" import")+8:-1].split(", ")
                importedfilelines = []
                for objti in objtoimport:
                    importedfilelines.append("from artiq.gateware."+importpath+" import "+ objti.strip()+"\n")
                filelinesidx = idx
                for ifl in importedfilelines:
                    filelines.insert(idx,ifl)
                    idx = idx + 1
                print("Found import multi-objects \n")
                continue
            else:
                ifo = ImportFileObject(fl)
                existedimportedobject = False
                for ipob in importedobject:
                    if len(set(ipob) & set(ifo.objectlist)) == len(set(ifo.objectlist)):
                        existedimportedobject = True
                if existedimportedobject:
                    continue
                importedobject.append(ifo.objectlist)
                f = open(ifo.objectfilepath,"r")
                importedfilelines = f.readlines()
                filelinesidx = idx
                for ifl in importedfilelines:
                    filelines.insert(idx,ifl)
                    idx = idx + 1
                print(ifo.objectlist)
                print(currentobjectlist)
                filelines.insert(idx,"endofobject "+".".join(ifo.objectlist)+"\n")
                idx = idx + 1
                filelines.insert(idx,"startofobject "+".".join(currentobjectlist)+"\n")
                idx = idx + 1
                currentobjectlist = ifo.objectlist
                print("Found import an object \n")
                continue

        if fl.strip().startswith("endofobject"):
            if ".".join(currentobjectlist) != fl[12:].strip():
                print("ERROR object classes messed up!!!!")
        
        if fl.strip().startswith("startofobject"):
            currentobjectlist = fl[14:-1].split(".")

        if fl.strip().startswith("class"):
            classnamestart = fl.find(" ")
            classnameend = fl.find("(")
            if classnameend == -1:
                classnameend = fl.find(":")
            currentclassname = fl[classnamestart + 1:classnameend]
            classes.append(ArtiqClass(currentclassname, currentobjectlist))

            inheritanceend = fl.find(")")
            if inheritanceend != -1:
                inherit = fl[classnameend + 1:inheritanceend].split(",")
                for inh in inherit:
                    classes[-1].inheritance.content.append(inh.strip())
                    for cl in classes:
                        if cl.name == inh.strip():
                            classes[-1].submodules.inherit.extend(cl.submodules.inherit)
                            classes[-1].signals.inherit.extend(cl.signals.inherit)
                            classes[-1].clockdomains.inherit.extend(cl.clockdomains.inherit)
                            classes[-1].objects.inherit.extend(cl.objects.inherit)
                            classes[-1].functions.inherit.extend(cl.functions.inherit)
                            classes[-1].submodules.inherit.extend(cl.submodules.content)
                            classes[-1].signals.inherit.extend(cl.signals.content)
                            classes[-1].clockdomains.inherit.extend(cl.clockdomains.content)
                            classes[-1].objects.inherit.extend(cl.objects.content)
                            classes[-1].functions.inherit.extend(cl.functions.content)
                            break

        if fl.startswith("    def"):
            functionnamestart = fl.find("d")
            functionnameend = fl.find("(")
            if functionnameend == -1:
                functionnameend = fl.find(":")
            currentfunctionname = fl[functionnamestart + 4:functionnameend]
            if "__init__" != currentfunctionname:
                classes[-1].functions.content.append(currentfunctionname)

        signalname = scancodesignature(fl,""," = Signal(","self.")
        if len(classes) > 0 and "" != signalname:
            classes[-1].signals.content.append(signalname)

        submodulename = scancodesignature(fl,"self.submodules += ","","self.submodules += ")
        if len(classes) > 0 and "" != submodulename:
            classes[-1].submodules.content.append(submodulename)

        submodulename = scancodesignature(fl,"self.submodules."," = ","self.submodules.")
        if len(classes) > 0 and "" != submodulename:
            classes[-1].submodules.content.append(submodulename)

        submodulename = scancodesignature(fl,"setattr(self.submodules, ","","setattr(self.submodules, ")
        if len(classes) > 0 and "" != submodulename:
            submodulename = submodulename.split(",")
            classes[-1].submodules.content.append(submodulename[0])

        clockdomainname = scancodesignature(fl,"self.clock_domains."," = ClockDomain(","self.clock_domains.")
        if len(classes) > 0 and "" != clockdomainname:
            classes[-1].clockdomains.content.append(clockdomainname)

    for cl in classes:
        cl.printclass()

    filenamepath = filenamepath.replace("\\","_")
    filenamepath = filenamepath.replace("/","_")
    rfilenamepathartiq = filenamepath.rfind("artiq")
    rfilenamepathdot = filenamepath.rfind(".")
    filename = filenamepath[rfilenamepathartiq:rfilenamepathdot]

    stl = SvgTextLine(16, 200)
    dwg = svgwrite.Drawing( filename+'.svg', profile='tiny')
    clg = dwg.g(id = "classdirectory")
    importedclasses = []
    for cl in classes:
        importedclasses = []
        importedclasses.extend(cl.hierarchy)
        importedclasses.append(cl.name)
        print(".".join(importedclasses))
        clg.add(dwg.text(importedclasses, insert=(-400, stl.idx*stl.height), fill=svgwrite.rgb(0, 0, 0, 'RGB')))
        stl.idx = stl.idx + 1
    dwg.add(clg)

    stl.idx = 0
    for cl in classes:
        stl.idx = stl.idx + 3
        stl.rectstartidx = stl.idx - 1
        clg = dwg.g(id = cl.name)
        clg.add(dwg.text(".".join(cl.hierarchy)+"."+cl.name, insert=(10, stl.idx*stl.height), fill=svgwrite.rgb(0, 64, 64, 'RGB')))
        clg.add(dwg.line((0, stl.idx*stl.height + 4), (stl.length, stl.idx*stl.height + 4), stroke=svgwrite.rgb(0, 0, 0, 'RGB')))
        cl.inheritance.svgdrawobject(stl, dwg, clg)
        cl.functions.svgdrawobject(stl, dwg, clg)
        cl.signals.svgdrawobject(stl, dwg, clg)
        cl.clockdomains.svgdrawobject(stl, dwg, clg)
        cl.submodules.svgdrawobject(stl, dwg, clg, True)
        clg.add(dwg.rect(insert=(0,stl.rectstartidx*stl.height),size=(stl.length,stl.height*(stl.idx - stl.rectstartidx + 1)),fill="none", stroke=svgwrite.rgb(0, 0, 0, 'RGB'), stroke_width=1))
        dwg.add(clg)
    dwg.save()
    

if __name__ == "__main__":
    main()