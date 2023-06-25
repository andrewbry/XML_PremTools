'''
ALE_WAV_replace_round_trip - alters ALE headers from Resolve, alters XML audio info from Premiere
(c) 2023 - Andrew Buckley

requires:  

'''

# import
import csv, os, datetime, time
from tkinter import *
from tkinter import filedialog, messagebox

# xml parser gui stuff
from xml.dom.minidom import parse
import xml.etree.ElementTree as ET



# Define UI
class ingestUI():
    def __init__(self):
        ############################
        # Create UI function
        ############################

        # initiate globals
        self.fileName = ''
        self.aleFileName = ''

        # assign the UI master
        self.master = Tk()
        self.master.geometry("900x150+200+200")
        self.master['background'] = '#191919'
        self.master.resizable(0, 0)
        self.outputfolder = ''

        # set the menu items
        self.master.title("Prem XML/ALE tools v1.4")


        # line 1 file dialogue
        self.frame3 = Frame(self.master)
        self.frame3['background'] = '#191919'
        self.labelextra = Label(self.frame3, text='xml should have video elements deleted, audio to be on mono tracks',
                                background='#191919',
                                foreground='white')
        self.frame3.pack(fill=X)
        self.labelextra.pack(side=TOP, padx=15, pady=(10, 0))

        self.frame1 = Frame(self.master)
        self.frame1['background'] = '#191919'
        self.label1 = Label(self.frame1, text='XML File', width=10, background='#666666')
        self.entry1 = Entry(self.frame1, background='#191919', foreground='white')
        self.button1 = Button(self.frame1, text='browse...', command=lambda: self.onOpen('xml'), background='#666666')
        self.frame1.pack(fill=X, pady=(0, 10))
        self.label1.pack(side=LEFT, padx=5)
        self.entry1.pack(side=LEFT, expand=YES, fill=X)
        self.button1.pack(side=RIGHT, padx=15)



        # line 2 file dialogue
        self.frame2 = Frame(self.master)
        self.frame2['background'] = '#191919'
        self.label2 = Label(self.frame2, text='ALE File', width=10, background='#666666')
        self.entry2 = Entry(self.frame2, background='#191919', foreground='white')
        self.button2 = Button(self.frame2, text='browse...', command=lambda: self.onOpen('ale'), background='#666666')
        self.frame2.pack(fill=X)
        self.label2.pack(side=LEFT, padx=5)
        self.entry2.pack(side=LEFT, expand=YES, fill=X)
        self.button2.pack(side=RIGHT, padx=15)

        # line 5 buttons
        self.frame5 = Frame(self.master)
        self.frame5['background'] = '#191919'
        self.btn3 = Button(self.frame5, text='Reset Defaults', command=self.setDefault, background='#666666')
        self.btn5 = Button(self.frame5, text='Analyse XML', state=DISABLED,
                           command=lambda: self.readFile('xml'), background='#888888')
        self.btn6 = Button(self.frame5, text='Analyse ALE', state=DISABLED,
                           command=lambda: self.readFile('ale'), background='#888888')

        self.btn3.pack(side=LEFT, padx=(50, 0))
        self.btn5.pack(side=RIGHT, padx=(0, 50))
        self.btn6.pack(side=RIGHT, padx=(0, 50))
        self.frame5.pack(fill=X, pady=(10, 0))

    def onOpen(self, input_type):
        if input_type == 'xml':
            f_types = [('XML Files', '*.xml'), ('All files', '*')]
            dlg = filedialog.Open(self.master, filetypes=f_types)
            fl = dlg.show()
            if fl != '':
                self.entry1.delete(0, END)
                self.entry1.insert(INSERT, os.path.basename(fl))
                self.fileName = fl
                self.validateEntry()
        elif input_type == 'ale':
            f_types = [('ALE Files', '*.ale'), ('All files', '*')]
            dlg = filedialog.Open(self.master, filetypes=f_types)
            al = dlg.show()
            if al != '':
                self.entry2.delete(0, END)
                self.entry2.insert(INSERT, os.path.basename(al))
                self.aleFileName = al
                self.validateEntry()

    def setDefault(self):
        self.fileName = ''
        self.aleFileName = ''
        self.entry1.delete(0, END)
        self.entry2.delete(0, END)
        self.btn5.config(state=DISABLED)
        self.btn6.config(state=DISABLED)
        return

    def validateEntry(self):
        # print(self.var2.get())
        if self.fileName != '':
            self.btn5.config(state=NORMAL)
            return True

        else:
            self.btn5.config(state=DISABLED)

        if self.aleFileName != '':
            self.btn6.config(state=NORMAL)
            return True

        else:
            self.btn6.config(state=DISABLED)

        return False

    def readFile(self, type):
        # print(type)

        # validate entries and collect files
        if self.validateEntry() is True and type == 'xml':
            # print('here')
            # self.outputfolder = filedialog.askdirectory(title="Output Directory")

            f = ingest.collect_clip_info(self.fileName)
            if f == 0:
                messagebox.showinfo("Warning", "Something went wrong. Couldn't fix any clips.")
                self.setDefault()
                return

            self.setDefault()

            messagebox.showinfo("Success", "Fixed {0} clip names!".format(f))
        elif self.validateEntry() is True and type == 'ale':
            # print(self.aleFileName)
            l = aleingest.rename_ale_columns(self.aleFileName)
            if l == 0:
                messagebox.showinfo("Warning", "Something went wrong. Couldn't fix any columns.")
                self.setDefault()
                return

            self.setDefault()

            messagebox.showinfo("Success", "Fixed {0} column names!".format(l))
        else:
            messagebox.showinfo("Warning", "This is not a valid entry!")
        return


class IngestApp:
    def __init__(self):
        # initiate globals
        # csv.register_dialect('myDialect', delimiter=',', lineterminator='\n')
        pass

    def collect_clip_info(self, xmlf):
        ############################
        # Begin Parsing XML File initialise variables
        ############################

        tree = ET.parse(xmlf)
        myroot = tree.getroot()
        numberofclipitems = 0
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')

        for audioclipitem in myroot.findall("./sequence/media/audio/track/clipitem"):
            clipname = audioclipitem.find("name")
            name = audioclipitem.find("./file/name")
            origa = audioclipitem.find("./logginginfo/originalaudiofilename")
            audiopath = origa.text
            try:
                audioname = audiopath.split("\\")
            except AttributeError:
                continue

            # audioname = audiopath.split("\\")
            # masterclip = audioclipitem.find("masterclipid")
            # justpath = audiopath.replace(audioname[-1], '')
            # origv = audioclipitem.find("./logginginfo/originalvideofilename")

            clipname.text = audioname[-1]

            # only change the file name and path we it's available
            if not name:
                try:
                    print('Correcting: ' + name.text + " --> " + audioname[-1])
                    filepath = audioclipitem.find("./file/pathurl")
                    name.text = audioname[-1]
                    color = audioclipitem.find("./labels/label2")
                    color.text = "Caribbean"
                    # filepath.text = audiopath.replace('\\', '/')
                    # filepath.text = justpath.replace('\\', '/')
                    # filepath.text = ''
                    filepath.text = audioname[-1]
                    numberofclipitems += 1

                except AttributeError:
                    continue

        flwr = xmlf.replace('.xml', '-MOD-' + st + '.xml')

        tree.write(flwr)
        return numberofclipitems

class AleRename:
    def __init__(self):
        # initiate globals
        pass

    def rename_ale_columns(self, alef):
        columns = {'Name': 'UNC',
                   'UNC': 'FilePath',
                   'Auxiliary TC1': 'Sound TC',
                   'Source File Path': 'ImageFileName',
                   'Display Name': 'Name',
                   'Sync Audio': 'AudioFileName'}

        ALEout = []
        ALEin = []
        corrected = 0

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')

        with open(alef, mode='r', newline='', encoding='utf-8') as a:
            t = csv.reader(a, delimiter='\t')

            currentLine = 0
            user = 'No'
            for line in t:
                # start recording new ale
                # use list to break reference
                ALEout.insert(currentLine, list(line))
                ALEin.insert(currentLine, line)

                # this is the headers
                if currentLine == 7 and line[0] == 'Name':
                    itemPos = 0
                    for item in line:
                        # print(item)
                        for key, value in columns.items():
                            if item == key:
                                if key == 'UNC':
                                    # record position for renaming
                                    UNCitemPos = itemPos
                                print('Correcting: ' + ALEout[currentLine][itemPos] + " --> " + value)
                                ALEout[currentLine][itemPos] = value
                                corrected += 1
                                continue
                        itemPos += 1

                if currentLine > 9 and "_001.R3D" in line[UNCitemPos]:
                    # prompt user to fix R3D names if found one
                    if user == 'No':
                        user = messagebox.askquestion('Found R3D files!?',
                                                      'Do you want to remove the "_001" from the R3D file path names?',
                                                      icon='warning')
                    if user == 'yes':
                        print('Correcting: ' + ALEout[currentLine][UNCitemPos] + " --> " + ALEout[currentLine][UNCitemPos].replace("_001.R3D", ".R3D"))
                        ALEout[currentLine][UNCitemPos] = ALEout[currentLine][UNCitemPos].replace("_001.R3D", ".R3D")
                    else:
                        continue

                currentLine += 1

        # create our output name and timestamp it
        flwr = alef.replace('.ale', '-MOD-' + st + '.ale')

        # make our output file
        if corrected > 0:
            with open(flwr, mode='w', newline='', encoding='utf-8') as w:
                writer = csv.writer(w, delimiter='\t')

                # write our rows to file
                for wrow in ALEout:
                    writer.writerow(wrow)

        return corrected


my_gui = ingestUI()
ingest = IngestApp()
aleingest = AleRename()
my_gui.master.mainloop()
