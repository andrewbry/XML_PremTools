# XML Premiere Tools

These are a few python scripts for analysing XMLs or ALEs from Premiere

## ALE_WAV_replace_roundTrip 
This tool was in a specific workflow to convert the headers on an ALE coming from Davinci Resolve that has had sound synced rendered for use in Premiere as Poxies.
The the proxies are rendered as ProRes with the multichannel synced audio. A ALE is exprted from Resolve, ran through this tool and the ALE is imported into Premiere and the clips are then linked.
This tool addresses the heading mismatch of what Premiere accepts for metadata setup on the clips.
Through this scene and take names can be used that have been setup in Resolve and also original audio clip names and timecode can be stored as well.

Specifically it changes these columns.
'Name' -> 'UNC',
'UNC' -> 'FilePath',
'Auxiliary TC1' -> 'Sound TC',
'Source File Path' -> 'ImageFileName',
'Display Name' -> 'Name',
'Sync Audio' -> 'AudioFileName'

At the end of the edit The original WAV files can be relinked by exporting a clean XML from Premiere (no video elements, only the audio from poxies to be swapped)
It's then ran through the XML part of the tool. The XML is imported and the RAW WAV files can be swapped for the proxie audio. This is so the RAW audio can be exported as ALE for use in ProTools, keeping all metadata.

## xml_shottracker_list
This tool was made to track VFX shots in edits made in Premiere. VFX tag names were made on a specific video layer above the shot. This is done using the text effect in Premiere on a transparent layer.
Ideally there is 1 layer of video which has the slate clip used in the vfx shot. The XML is exported, an MP4 can also be exported from the start of the timeline to it aligns to the XML.
Once selected in the script UI, you set which video layer has the tags and which video layer has the slate clips. The XML is analysed to find which slates fit inside the tag layers in/out. 
The following info is recorded and put into a csv spreadsheet.

Thumbnail - if an mp4 was provided
Shot name - The first text element text of the vfx shot tag
Editorial Notes - The first text element text of the vfx shot tag 
Slates - the clip names inside the vfx shot tag
Tape Name - tape names of the clips inside the vfx shot tag
Duration - durations of the clips
Scale - any scale info in the slate clips
Retime - any retime info on the slate clips

requires:  xlsxwriter, ffmpeg


