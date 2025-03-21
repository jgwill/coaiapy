from coaiamodule import readconfig_polly
import boto3

def synthesize(text,voice_id,outfile,outformat="mp3"):
	key,secret,region=readconfig_polly()
	
	try:
		polly = boto3.client('polly', aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)
		
		response = polly.synthesize_speech(Text=text,OutputFormat=outformat,VoiceId=voice_id)
	except Exception as ex :
		print(' error with polly service')
		print(ex)
		raise ex 
	
	try:
		file = open(outfile, 'wb')
		file.write(response['AudioStream'].read())
		file.close()
	except Exception as ex :
		print('  error when writing the file '+outfile)
		print(ex)
		raise ex 
		
