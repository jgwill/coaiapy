coaia.transcriber.py

* It imports the transcribe_audio from coaiamodule and is a file I updated to transcribe from iOS Shortcut or Run manually, I dont remember  (see: dowork(fn+ext,dir_root,None))

```python

import sound
from coaiamodule import transcribe_audio
import os
import sys


#@STCGoal proto to travscribe amd audio tontext


#@STCIssue I guess this has the goal of transcribing a received audio file to a target text in Cli modality.

fn='sc-240429-part-002-audio-story'
fn='nauk-what-is-fd'#nauk-what-is-fd.m4a
#fn='fuck'

ext='.mp3'
ext='.m4a'

dir_root='../../shared/pto'
dir_root='../../shared/CeSaReT/2tr'


dir_root='../../shared/na'

#dir_root='.'
print(os.getcwd())


def dowork(filename,indir=None,outdir=None):
	print('========================')
	
	print(' filename:',filename)
	if indir is not None:
	  print(' indir:',indir)
	  audio_file_path=os.path.join(indir,filename)
	else:
	  audio_file_path=filename
	
	texfn=filename.replace('.m4a','').replace('.mp3','').replace('.wav','')+'.c.txt'
	print('  texfn:',texfn)
	try:
		transcribed_text = transcribe_audio(audio_file_path)
		
		if outdir is None or outdir=='' or outdir=='.' or outdir=='./':
			
			print( ' outdir == indir ')
			text_file_path=os.path.join(indir,texfn)
		else:
			print('  outdir:',outdir)	
			if not os.path.exists(outdir):
				os.makedirs(outdir)
			text_file_path=os.path.join(outdir,texfn)
		
		
		
			
		print('"""')
		print(transcribed_text)
		print('"""')
		
		# Set the transcribed text in the text view
		
		
		#write the text file 
		print(' text_file_path:',text_file_path)
		
		with open(text_file_path, 'w',encoding='utf-8') as file:
			file.write(transcribed_text)
			print('Saved:'+text_file_path)
		
	
			
	
	except Exception as e:
		
		print(e)
		
#dowork('ddm-sess2404271549-003.m4a','../../shared/ddm-samples/recording','../../shared/ddm-samples/output')


#dowork(fn+'.m4a','../../shared/pto','../../shared/pto/output')
dowork(fn+ext,dir_root,None)

#dowork(fn+ext,None,None)
```