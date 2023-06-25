'''
xml_shottracker - analyses XML files from Adobe Premiere to get tagged VFX shots slate metadata and edit info.
(c) 2023 - Andrew Buckley

requires:   xlsxwriter, ffmpeg

'''

# import
import csv, os, datetime, time
from tkinter import *
from tkinter import filedialog, messagebox
import subprocess
import xlsxwriter

# xml parser gui stuff
from xml.dom.minidom import parse


# Define UI
class ingestUI():
    def __init__(self):
        ############################
        # Create UI function
        ############################

        # initiate globals
        # self.output_folder = ''
        self.fileName = ''
        self.offlinev = ''

        # assign the UI master
        self.master = Tk()
        self.master.geometry("900x150+200+200")
        self.master.resizable(0, 0)
        self.var2 = IntVar()
        self.vidlay = IntVar()
        self.taglay = IntVar()
        self.outputfolder = ''

        # set the menu items
        self.master.title("Premiere XML Shot Logger")

        # line 1 file dialogue
        self.frame1 = Frame(self.master)
        self.label1 = Label(self.frame1, text='XML File', width=15)
        self.entry1 = Entry(self.frame1)
        self.button1 = Button(self.frame1, text='browse...', command=lambda: self.onOpen('xml'))
        self.frame1.pack(fill=X)
        self.label1.pack(side=LEFT)
        self.entry1.pack(side=LEFT, expand=YES, fill=X)
        self.button1.pack(side=RIGHT, padx=15)

        # Line 2 check box options
        # collect thumbnails?
        self.frame2 = Frame(self.master)
        self.chkbx = Checkbutton(self.frame2, text="Thumbnails", variable=self.var2,
                                 onvalue=1, offvalue=0, command=lambda: self.validateEntry())
        self.entry2 = Entry(self.frame2)
        self.button2 = Button(self.frame2, text='browse...', command=lambda: self.onOpen('mp4'))
        self.frame2.pack(fill=X)
        self.chkbx.pack(side=LEFT, padx=10)
        self.entry2.pack(side=LEFT, expand=YES, fill=X)
        self.button2.pack(side=RIGHT, padx=15)

        # Line 3 number of video levels to check
        self.frame3 = Frame(self.master)
        self.label3 = Label(self.frame3, text='Slate video layer:', width=14)
        self.s = Spinbox(self.frame3, from_=1, to=5, width=3, textvariable=self.vidlay)
        self.frame3.pack(fill=X, pady=(10, 0))
        self.s.pack(side=RIGHT, padx=(0, 90))
        self.label3.pack(side=RIGHT)

        # Line 4 number of video levels to check
        self.frame4 = Frame(self.master)
        self.label4 = Label(self.frame4, text='Tag video layer:', width=13)
        self.s2 = Spinbox(self.frame4, from_=1, to=15, width=3, textvariable=self.taglay)
        self.frame4.pack(fill=X, pady=(2, 0))
        self.s2.pack(side=RIGHT, padx=(0, 90))
        self.label4.pack(side=RIGHT)

        # line 5 buttons
        self.frame5 = Frame(self.master)
        self.btn3 = Button(self.frame5, text='Reset Defaults', command=self.setDefault)
        self.btn5 = Button(self.frame5, text='Analyse', state=DISABLED,
                           command=self.readFile)
        # self.progressbar = ttk.Progressbar(self.frame5, orient=HORIZONTAL,
        #                                    length=200, mode='determinate', value=0)

        self.btn3.pack(side=LEFT, padx=(50, 0))
        # self.progressbar.pack(side=LEFT, padx=(50, 0))
        # self.progressbar.stop()
        self.btn5.pack(side=RIGHT, padx=(0, 50))
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
        elif input_type == 'mp4':
            f_types = [('Mp4 Files', '*.mp4'), ('Mov Files', '*.mov'), ('All files', '*')]
            dlg = filedialog.Open(self.master, filetypes=f_types)
            fl = dlg.show()
            if fl != '':
                self.entry2.delete(0, END)
                self.entry2.insert(INSERT, os.path.basename(fl))
                self.offlinev = fl
                self.validateEntry()

    def setDefault(self):
        self.fileName = ''
        self.offlinev = ''
        self.entry1.delete(0, END)
        self.entry2.delete(0, END)
        self.btn5.config(state=DISABLED)
        return

    def validateEntry(self):
        # print(self.var2.get())
        if self.var2.get() == 1:
            if self.offlinev is not '' and self.fileName is not '':
                self.btn5.config(state=NORMAL)
                return True
            else:
                self.btn5.config(state=DISABLED)
                return False

        elif self.fileName is not '':
            self.btn5.config(state=NORMAL)
            return True

        else:
            self.btn5.config(state=DISABLED)
        return False

    def readFile(self):

        # validate entries and collect files
        if self.validateEntry() is True:
            self.outputfolder = filedialog.askdirectory(title="Output Directory")

            f = ingest.collect_clip_info(self.fileName,
                                         self.offlinev,
                                         self.vidlay.get(),
                                         self.var2.get(),
                                         self.taglay.get(),
                                         self.outputfolder)
            if f == 0:
                messagebox.showinfo("Warning", "Didn't find any shots maybe tag layer is wrong?")
                return

            self.setDefault()

            messagebox.showinfo("Success", "Your XML has {0} shots!".format(len(f)))
        else:
            messagebox.showinfo("Warning", "This is not a valid entry!")
        return


############################
# process XML Function #
############################

class IngestApp:
    def __init__(self):
        # initiate globals
        csv.register_dialect('myDialect', delimiter=',', lineterminator='\n')
        pass

    def collect_clip_info(self, xmlf, offlinef, videotrack, thumbs, tagtrack, output):
        ############################
        # Begin Parsing XML File initialise variables
        ############################
        dom = parse(xmlf)

        sequences = []
        sequence_objects = []
        # Set optional effect parameters to False
        timeremap_value = 'na'
        scale_value = 'na'
        x_move = 'na'
        y_move = 'na'
        rotation_value = 'na'
        # This value gets set for each clip in the timeline
        seq_clip_number = 1
        shots = {}
        shots_update = {}
        clips = {}
        clip_reel = ''
        images = []

        # Makes a list of all sequence names
        for seq in dom.getElementsByTagName('sequence'):
            if seq.getElementsByTagName('name')[0].firstChild.data:
                print("Sequences are: ", seq.getElementsByTagName('name')[0].firstChild.data)
                sequence_objects.append(seq)
            else:
                continue

        # set and get main sequence properties
        main_seqobj = sequence_objects[0]
        seq_res_x = int(main_seqobj.getElementsByTagName('format')[0].getElementsByTagName('width')[0].firstChild.data)
        seq_res_y = int(main_seqobj.getElementsByTagName('format')[0].getElementsByTagName('height')[0].firstChild.data)
        sequence_fps = int(main_seqobj.getElementsByTagName('timebase')[0].firstChild.data)
        if main_seqobj.getElementsByTagName('rate')[0].getElementsByTagName('ntsc')[0].firstChild.data == 'TRUE':
            sequence_fps = round(sequence_fps / 1.001, 3)

        # set video track of the tags
        track = main_seqobj.getElementsByTagName('track')[tagtrack-1]

        # log tags on the user selected layer
        for tag in track.getElementsByTagName('clipitem'):
            # only if we have a text layer otherwise continue
            try:
                if tag.getElementsByTagName('effect')[0].childNodes[1].firstChild.data == 'Basic Motion' or \
                        tag.getElementsByTagName('effect')[0].childNodes[1].firstChild.data == 'Time Remap' or \
                        tag.getElementsByTagName('effect')[0].childNodes[1].firstChild.data == 'Vector Motion':
                    try:
                        shot_name = tag.getElementsByTagName('effect')[1].childNodes[1].firstChild.data
                        try:
                            shot_description = tag.getElementsByTagName('effect')[2].childNodes[1].firstChild.data
                        except AttributeError:
                            continue
                    except IndexError:
                        continue
                else:
                    shot_name = tag.getElementsByTagName('effect')[0].childNodes[1].firstChild.data
                    shot_description = tag.getElementsByTagName('effect')[1].childNodes[1].firstChild.data
            except IndexError:
                continue
            tagid = tag.getElementsByTagName('masterclipid')[0].firstChild.data
            shot_id = tag.getElementsByTagName('name')[0].firstChild.data
            shot_in = int(tag.getElementsByTagName('start')[0].firstChild.data)
            shot_out = int(tag.getElementsByTagName('end')[0].firstChild.data)
            shot_duration = shot_out - shot_in

            # log the clips as a dictionary
            shots[shot_name] = {
                'tagid': tagid,
                'name': shot_name,
                'description': shot_description,
                'in': shot_in,
                'out': shot_out,
                'duration': shot_duration,
            }

        # check if we found anything otherwise maybe video layer is wrong
        if len(shots) == 0:
            return 0

        # now look at video layer one // we can go up layers here // how to we log more than 1 clip per shot?
        for v in range(0, videotrack):
            slatetrack = main_seqobj.getElementsByTagName('track')[v]
            for clip in slatetrack.getElementsByTagName('clipitem'):
                masterclipid = clip.getElementsByTagName('masterclipid')[0].firstChild.data
                clip_slate = clip.getElementsByTagName("name")[0].firstChild.data
                start_point = int(clip.getElementsByTagName('start')[0].firstChild.data)
                end_point = int(clip.getElementsByTagName('end')[0].firstChild.data)
                clip_duration = int(clip.getElementsByTagName("duration")[0].firstChild.data)

                # get file reel name
                try:
                    clip_reel = clip.getElementsByTagName('reel')[0].getElementsByTagName('name')[0].firstChild.data
                except IndexError:
                    # if the clip isnt a master clip search the whole xml for its master clip and get the path
                    print('Failed to get masterclip info', clip_slate,
                          '. Searching other clipitems for matching name.')
                    for m_clip in dom.getElementsByTagName('clipitem'):
                        if m_clip.getElementsByTagName('masterclipid')[0].firstChild.data == masterclipid:
                            try:
                                clip_reel = m_clip.getElementsByTagName('reel')[0].getElementsByTagName('name')[0].firstChild.data
                            except IndexError:
                                print('Failed too get pathurl, settings defaults')
                                clip_reel = 'none'
                            print("found the master clip information")
                            break
                        else:
                            print('Failed too get pathurl, settings defaults')
                            clip_reel = 'not found'

                # try to get any effects on the shots and log it
                # Get all effects applied to this clip
                for effect in clip.getElementsByTagName('effect'):
                    try:
                        effect_name = effect.childNodes[1].firstChild.data
                    except AttributeError:
                        effect_name = 'none'
                    if effect_name == 'Time Remap':
                        # Loop through all parameters of the effect
                        for param in effect.getElementsByTagName('parameter'):
                            param_id = param.childNodes[1].firstChild.data
                            if param_id == 'speed':
                                timeremap_value = param.getElementsByTagName('value')[0].firstChild.data
                                print(effect_name, param_id, timeremap_value)

                    # XML does hold key frame data for this effect. Could map this to another list 0 = scale, rotation, x, y
                    # need to check how the key frames work etc
                    if effect_name == 'Basic Motion':
                        for param in effect.getElementsByTagName('parameter'):
                            param_id = param.childNodes[1].firstChild.data
                            if param_id == 'scale':
                                scale_value = param.getElementsByTagName('value')[0].firstChild.data
                                print(effect_name, param_id, scale_value)
                            if param_id == 'rotation':
                                rotation_value = float(
                                    param.getElementsByTagName('value')[0].firstChild.data)
                                print(effect_name, param_id, rotation_value)
                            if param_id == 'center':
                                x_move = float(
                                    param.getElementsByTagName('value')[0].childNodes[1].firstChild.data)
                                y_move = float(
                                    param.getElementsByTagName('value')[0].childNodes[3].firstChild.data)
                                print(effect_name, param_id, x_move, y_move)
                                '''
                                So.... Figuring out how Premiere handles position values:
                                Prem 0-0 clip is centered upper left: value = .5,.5
                                prem 1920-1080, clip is centered lower right: value = .5 .5??
                                prem 1060-640, value: 0.052083 0.092593
                                prem center bottom: 960-1080, value: 0.0 0.5
                                prem center top: 960 0, value: 0.0 -0.5
                                prem UR 1919 0, value: 0.499479 -0.5

                                location 	x, y
                                center 		0, 0
                                UL			-0.5, -0.5
                                UR 			0.5, -0.5
                                LR 			0.5, 0.5
                                LL 			0, 0.5
                                y-up is negative
                                x-right is positive
                                The range from edge to edge of sequence space is 1. 
                                -.5 is left, .5 is right. 
                                -.5 is up, .5 is down.
                                .125, 0 would be 1200x540 = (seq_res_x * x_move) = how many pixels to move from center) = 1920*.125 + 1920/2 = 1200
                                for x: seq_res_x * x_move
                                for y: seq_res_y * -y_move
                                '''

                clip_id = "{0}_{1}".format(clip_slate, seq_clip_number)
                clips[clip_id] = {
                    'clipid': masterclipid,
                    'slate': clip_slate,
                    'reel': clip_reel,
                    'clipnumber': seq_clip_number,
                    'in': start_point,
                    'out': end_point,
                    'duration': clip_duration,
                    'retime': timeremap_value,
                    'scale': scale_value,
                    'x_move': x_move,
                    'y_move': y_move,
                    'rotation': rotation_value
                }

                timeremap_value = 'na'
                scale_value = 'na'
                x_move = 'na'
                y_move = 'na'
                rotation_value = 'na'
                seq_clip_number += 1

        # now we have our tags and 1 video layer to check against
        # go through the shots and see if any slates fit in it and then save it to put back into the shot info
        # duplicate our shots for update
        shots_update = shots

        for key, file_info in shots.items():
            si = file_info['in']
            so = file_info['out']

            slates = []
            reels = []
            scales = []
            retimes = []
            tempslate = []
            tempreel = []
            matches = 0
            tremap = []
            scmap = []

            for clip, clip_info in clips.items():
                print(tempslate)
                print(" ")
                print(slates)

                ci = clip_info['in']
                co = clip_info['out']

                if (si <= ci <= so) and (so >= co >= si):
                    if matches > 0:
                        tempslate.append(clip_info['slate'])
                        tempreel.append(clip_info['reel'])
                        tremap.append(clip_info['retime'])
                        scmap.append(clip_info['scale'])

                        slates[-1] = tempslate
                        reels[-1] = tempreel
                        scales[-1] = scmap
                        retimes[-1] = tremap
                    else:
                        tempslate.append(clip_info['slate'])
                        tempreel.append(clip_info['reel'])
                        tremap.append(clip_info['retime'])
                        scmap.append(clip_info['scale'])

                        slates.append(tempslate)
                        reels.append(tempreel)
                        scales.append(scmap)
                        retimes.append(tremap)
                        matches += 1

            # if we find a slated shot to put in put it in otherwise log none found
            if len(slates) > 0:
                shots_update[key].update(slate=slates[0])
                shots_update[key].update(reel=reels[0])
                shots_update[key].update(scale=scales[0])
                shots_update[key].update(retime=retimes[0])
            else:
                shots_update[key].update(slate=['none found'])
                shots_update[key].update(reel=['none found'])
                shots_update[key].update(scale=['na'])
                shots_update[key].update(retime=['na'])

        print("FINISHED - here's what we have")
        for key, file_info in shots_update.items():
            # check for incomplete sequences again
            print(key)
            print(file_info)

        if thumbs:
            for key, file_info in shots_update.items():
                # time.sleep(2)
                ti = file_info['in']
                to = file_info['out']
                # middle frame
                tm = int(((to - ti)/2) + ti)
                # thumbnail_maker(offlinef, tm, key, output)

                video_input_path = offlinef
                img_output_path = '{0}/{1}.jpg'.format(output, key)
                framenumber = "select=eq(n\\, {0})".format(tm)
                print(img_output_path)
                p1 = subprocess.Popen(
                    ['ffmpeg', '-y', '-i', video_input_path, '-vf', framenumber, '-s', '96x54', '-vframes', '1',
                     img_output_path])
                p1.communicate()



        e = create_log(shots_update, output, thumbs)
        return e


def thumbnail_maker(f, tc, name, fo):
    ############################
    # collect thumbnails function #
    ############################
    # go through each op
    video_input_path = f
    img_output_path = '{0}/{1}.jpg'.format(fo, name)
    framenumber = "select=eq(n\\, {0})".format(tc)
    print(img_output_path)
    p1 = subprocess.Popen(
        ['ffmpeg', '-y', '-i', video_input_path, '-vf', framenumber, '-s', '96x54', '-vframes', '1', img_output_path])
    p1.communicate()
    return


def create_log(shot_info, fo, thumbs):
    ############################
    # Now the xml has been parsed we need to log this information in an optical list #
    ############################

    # Create an new Excel file and add a worksheet.
    # we should prompt for location of the output / thumbs
    workbook = xlsxwriter.Workbook('{0}/images_{1}.xlsx'.format(fo, time_stamp()))
    worksheet = workbook.add_worksheet()
    shots = []

    # Widen the first column to make the text clearer.
    trow = 0
    tcol = 0
    worksheet.set_column(trow, tcol, 20)
    worksheet.set_row(trow, 50)
    worksheet.write(trow, tcol, 'Thumbnail')
    worksheet.write(trow, tcol + 1, 'Shot name')
    worksheet.write(trow, tcol + 2, 'Editorial Notes')
    worksheet.write(trow, tcol + 3, 'Slates')
    worksheet.write(trow, tcol + 4, 'Tape Name')
    worksheet.write(trow, tcol + 5, 'Duration')
    worksheet.write(trow, tcol + 6, 'Sequence')
    worksheet.write(trow, tcol + 7, 'Scale')
    worksheet.write(trow, tcol + 8, 'Retime')

    for key, file_info in shot_info.items():
        trow += 1
        worksheet.set_column(trow, tcol, 20)
        worksheet.set_row(trow, 50)
        if thumbs:
            thumbnail_path = '{0}/{1}.jpg'.format(fo, key)
            worksheet.insert_image(trow, tcol, thumbnail_path)
        worksheet.write(trow, tcol + 1, file_info['name'])
        worksheet.write(trow, tcol + 2, file_info['description'])
        worksheet.write(trow, tcol + 3, '\n'.join(file_info['slate']))
        worksheet.write(trow, tcol + 4, '\n'.join(file_info['reel']))
        worksheet.write(trow, tcol + 5, file_info['duration'])
        #worksheet.write(trow, tcol + 6, file_info['duration'])
        worksheet.write(trow, tcol + 7, '\n'.join(file_info['scale']))
        worksheet.write(trow, tcol + 8, '\n'.join(file_info['retime']))
        shots.append(file_info['name'])

    workbook.close()

    return shots


def time_stamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')
    return st


my_gui = ingestUI()
ingest = IngestApp()
my_gui.master.mainloop()




