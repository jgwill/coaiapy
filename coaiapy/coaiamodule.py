import requests
import json
import os
import markdown
import redis
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# version in pyrec prod
config=None


def find_existing_config():
  possible_locations = [
    '../../shared/etc/config.json',
    '../shared/etc/config.json',
    '../../etc/config.json',
    '../etc/config.json',
    '../config.json',
    '../config/config.json',
    './config.json',
    './etc/config.json'
  ]

  for location in possible_locations:
    if os.path.exists(location):
      return location

  return None
  
def read_config():
	global config
	# Load the config file
	#_cnf='../../shared/etc/config.json'
	_cnf = find_existing_config()
	
	if config is None:
		with open(_cnf) as config_file:
			config = json.load(config_file)
	return config


def render_markdown(markdown_text):
  """Renders markdown to HTML.
    Args:
      markdown_text: The markdown text to render.
    Returns:
      The HTML representation of the markdown text.
  """
  html = markdown.markdown(markdown_text)
  return html

#todo @STCGoal Utilities

def remove_placeholder_lines(text):
  # Split the text into lines
  lines = text.split('\n')
  # Iterate over the lines and remove lines starting with "Placeholder"
  cleaned_lines = [line for line in lines if not line.startswith("Placeholder")]
  
  # Join the cleaned lines back into a string
  cleaned_text = '\n'.join(cleaned_lines)
  
  return cleaned_text


#todo @STCGoal Section for transcribing audio to text
#todo @STCIssue Cant receive too large recording.  Split audio, transcribe and return one combinasion of inputs.

def transcribe_audio(file_path):
    global config
    read_config()
    # Read OpenAI API key from config.json
    
    openai_api_key = config.get('openai_api_key')

    # Constants
    openai_api_url = 'https://api.openai.com/v1/audio/transcriptions'

    # Set up headers and payload
    headers = {
        'Authorization': f'Bearer {openai_api_key}'
    }
    files = {'file': open(file_path, 'rb')}
    payload = {
        'model': 'whisper-1'
    }

    # Send audio data to OpenAI for transcription
    response = requests.post(openai_api_url, headers=headers, files=files, data=payload)
    response_json = response.json()
    transcribed_text = response_json.get('text')

    return transcribed_text


#todo @STCGoal Generic abstract for refactoring and simplification and extensibility speed up
def abstract_send(input_message, instructions_config_name,temperature_config_name=None,instructions_default='You are a helpful assistant',temperature=0.3,pre=''):
	global config
	
	read_config()
	
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	
	# Check if using config or default values for temperature and preprompt_instruction
	
	temperature = config[temperature_config_name] if temperature is None else temperature
		
	system_instruction = config.get(instructions_config_name, instructions_default)
	if instructions_default==system_instruction:
	  print('coaiamodule::  instructions_default USED')
	# Concatenate preprompt_instruction with input_message
	
	content=input_message
	
	if pre != '':
	  content=pre + ' '+input_message 
    
  # Create the request JSON payload
  
	payload = {
        "model": model,
        "messages": [{"role": "user", "content": content},{"role": "system", "content": system_instruction}],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Retrieve the completed message from the response
		
		completed_message = response.json()['choices'][0]['message']['content']
		return completed_message
	else:
		# Handle the error case
		print('Error:', response.text)
		return None

#todo Feature to call with just one word corresponding to the process step define in config.  future extension will trigger a define process instructions and temperature. see: coaiauimodule for more on the feature design
def abstract_process_send(process_name,input_message,default_temperature=0.35,pre=''):
  instruction_config_name=process_name+'_instruction'
  temperature_config_name=process_name+'_temperature'
  #def abstract_send(input_message, instructions_config_name,temperature_config_name=None,instructions_default='You are a helpful assistant',temperature=0.3,pre=''):
  return abstract_send(input_message,instruction_config_name,temperature_config_name,temperature=default_temperature,pre=pre)
#abstract_send(input_message, instructions_config_name,temperature_config_name=None,instructions_default='You are a helpful assistant',temperature=0.3,pre=''):

def csv2json(input_message, temperature=None,pre=''):
  instructions_config_name='csv2json_instruction'
  temperature_config_name='csv2json_temperature'
  return abstract_send(input_message,instructions_config_name,temperature_config_name)

#summarizer_instruction
def summarizer(input_message, temperature=None,pre=''):
  instructions_config_name='summarizer_instruction'
  temperature_config_name='summarizer_temperature'
  return abstract_send(input_message,instructions_config_name,temperature_config_name)

#todo @STCGoal CSV2json
#transform this CSV content into json (encapsulate output and don't comment it) :
#csv2json_instructions
#csv2json_temperature
def csv2json_legacy(input_message, temperature=None,pre=''):
	global config
	
	read_config()
	
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	
	# Check if using config or default values for temperature and preprompt_instruction
	
	temperature = config['csv2json_temperature'] if temperature is None else temperature
		
	system_instruction = config.get('csv2json_instruction', "transform this CSV content into json (encapsulate output and don't comment it) :") 
	
	
  # Concatenate preprompt_instruction with input_message
  
	content=pre + ' '+input_message
  
  # Create the request JSON payload
  
	payload = {
        "model": model,
        "messages": [{"role": "user", "content": content},{"role": "system", "content": system_instruction}],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Retrieve the completed message from the response
		
		completed_message = response.json()['choices'][0]['message']['content']
		return completed_message
	else:
		# Handle the error case
		print('Error:', response.text)
		return None
        
#todo @STCGoal detail2shape

def d2s_send(input_message, temperature=None,pre=''):
	global config
	
	read_config()
	
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	
	# Check if using config or default values for temperature and preprompt_instruction
	
	temperature = config['d2s_default_temperature'] if temperature is None else temperature
		
	system_instruction = config.get('d2s_instruction', 'You do : Receive a text that requires to put details into shapes. you keep the essence of what is discussed foreach elements you observe and able yo group in the inout text.') 
	
	
  # Concatenate preprompt_instruction with input_message
  
	content=pre + ' '+input_message
  
  # Create the request JSON payload
  
	payload = {
        "model": model,
        "messages": [{"role": "user", "content": content},{"role": "system", "content": system_instruction}],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Retrieve the completed message from the response
		
		completed_message = response.json()['choices'][0]['message']['content']
		return completed_message
	else:
		# Handle the error case
		print('Error:', response.text)
		return None
        
  
#todo @STCGoal Dictkore

def dictkore_send(input_message, temperature=None,pre=''):
	global config
	
	read_config()
	
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	
	# Check if using config or default values for temperature and preprompt_instruction
	
	temperature = config['dictkore_default_temperature'] if temperature is None else temperature
		
	system_instruction = config.get('dictkore_instruction', 'You do : Receive a dictated text that requires correction and clarification.\n\n# Corrections\n\n- In the dictated text, spoken corrections are made. You make them and remove the text related to that to keep the essence of what is discussed.\n\n# Output\n\n- You keep all the essence of the text (same length).\n- You keep the same style.\n- You ensure annotated dictation errors in the text are fixed.') 
	
	
  # Concatenate preprompt_instruction with input_message
  
	content=pre + ' '+input_message
  
  # Create the request JSON payload
  
	payload = {
        "model": model,
        "messages": [{"role": "user", "content": content},{"role": "system", "content": system_instruction}],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Retrieve the completed message from the response
		
		completed_message = response.json()['choices'][0]['message']['content']
		return completed_message
	else:
		# Handle the error case
		print('Error:', response.text)
		return None
        
  

def llm(user,system, temperature=0.3):
	global config
	read_config()
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	

  
  # request JSON payload
	payload = {
        "model": model,
        "messages": [
          {"role": "system", "content": system},
          {"role": "user", "content": user}
          ],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

  # Check if the request was successful
	if response.status_code == 200:
  	
  	# Retrieve the completed message from the response
		completed_message = response.json()['choices'][0]['message']['content']
  	
		return completed_message
	else:
  	
  	# Handle the error case
  	
		print('Error:', response.text)
  	
		return None
   

#@STCGoal Section for text and chat
def send_openai_request(input_message, use_config=False, temperature=None, preprompt_instruction=None):
	global config
	read_config()
	openai_api_url = config['openai_api_url']
	openai_api_key = config['openai_api_key']
	model = config['model']
	
	# Check if using config or default values for temperature and preprompt_instruction
	
	if use_config:
		temperature = config.get('default_temperature', 0.7) if temperature is None else temperature
		
		preprompt_instruction = config.get('default_preprompt_instruction', '') if preprompt_instruction is None else preprompt_instruction
		
	else:
		temperature = 0.7 if temperature is None else temperature
		
		preprompt_instruction = '' if preprompt_instruction is None else preprompt_instruction
  
  # Concatenate
	content = preprompt_instruction + ' ' + input_message
  
  # request JSON payload
  
	payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature
        }
  # Send the request to the OpenAI API
	headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
        }
	response = requests.post(openai_api_url, json=payload, headers=headers)

  # Check if the request was successful
	if response.status_code == 200:
  	
  	# Retrieve the completed message from the response
		completed_message = response.json()['choices'][0]['message']['content']
  	
		return completed_message
	else:
  	
  	# Handle the error case
  	
		print('Error:', response.text)
  	
		return None
        

def send_openai_request_v4(input_message, use_config=False, temperature=None, preprompt_instruction=None,modelname="gpt-3.5-turbo"):
    global config
    # Load the config file
    read_config()

    openai_api_url = config['openai_api_url']
    openai_api_key = config['openai_api_key']
    
    # using config or default values for temperature and preprompt_instruction
    if use_config:
        temperature = config.get('default_temperature', 0.7) if temperature is None else temperature
        preprompt_instruction = config.get('default_preprompt_instruction', '') if preprompt_instruction is None else preprompt_instruction
    else:
        temperature = 0.7 if temperature is None else temperature
        preprompt_instruction = '' if preprompt_instruction is None else preprompt_instruction
    
    # preprompt_instruction with input_message
    content = preprompt_instruction + ' ' + input_message

    # request JSON payload
    payload = {
        "model": modelname,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature
    }

    # Send the request to the OpenAI API
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(openai_api_url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the completed message from the response
        completed_message = response.json()['choices'][0]['message']['content']
        return completed_message
    else:
        # Handle the error case
        print('Error:', response.text)
        return None

def generate_image(prompt,size=None,nb_img=1):
  global config
  read_config()
  #size of generated image
  if size is None:
    size=config["default_size"]
  api_key = config["pyapp_dalle_api_2405"] 

  # Set the API endpoint.
  api_endpoint = config["dalle_api_endpoint"]
  
  # Set the request headers.
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
  }
  
  # Set the request body.
  data = {
      "prompt": prompt,
      "n": nb_img,  # Number of images to generate.
      "size": size,  # Image size.
  }

  # Send the request.
  response = requests.post(api_endpoint, headers=headers, json=data)

  # Check for errors.
  if response.status_code != 200:
    raise Exception(f"Error: {response.status_code}")

  # Extract the image URLs from the response.
  image_urls = [image["url"] for image in response.json()["data"]]

  return image_urls
  


def send_openai_request_v3(input_message, temperature=0.7, preprompt_instruction=''):
    global config
    # Load the config file
    read_config()

    openai_api_url = config['openai_api_url']
    openai_api_key = config['openai_api_key']
    
    # preprompt_instruction with input_message
    content = preprompt_instruction + ' ' + input_message

    # request JSON payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature
    }

    # header
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(openai_api_url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the completed message from the response
        completed_message = response.json()['choices'][0]['message']['content']
        return completed_message
    else:
        # Handle the error case
        print('Error:', response.text)
        return None

        


#@STCGoal Tasher/Taler
def _newjtaler(jtalecnf):
  try:
    _r = redis.Redis(
    host=jtalecnf['host'],
    port=int(jtalecnf['port']),
    password=jtalecnf['password'],
    ssl=jtalecnf['ssl'])
    print('newjtaler servide created')
    return _r
  except Exception as e :
    print(e)
    print('error creating newjtaler')
    return None

def _taleadd(_r,k,c,quiet=False):
  try:
    _r.set(k, c)
    _kv=_r.get(k)
    if not quiet:
      print(_kv)
    return _kv
  except Exception as e :
    print(e)
    return None

def tash(k,v):
  
  _r=None
  try:
    #from coaiamodule import read_config
    jtalecnf=read_config()['jtaleconf']
    _r=_newjtaler(jtalecnf)
  except Exception as e:
    print(e)
    print('init error')
  if _r is not None:
    result=_taleadd(_r,k,v,True)
    if result is not None:
      print('Stashed success:'+k)
    else:
      print('Stashing failed')
    return result
  
