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
It's then ran through the XML part of the tool. The XML is imported and the RAW WAV files can be swapped for the proxie audio. This is so the RAW audio can be exported as ALE for use in ProTools.

