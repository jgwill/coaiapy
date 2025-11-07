import requests
import json
import os
import markdown
import redis
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# version in pyrec prod
config=None
_loaded_env_path=None  # Track which env_path was used to load config


def find_existing_config():
  # Priority order: current directory first, then HOME, then other locations
  priority_locations = [
    './coaia.json',  # Current directory - HIGHEST PRIORITY
  ]
  
  # Check priority locations first
  for location in priority_locations:
    if os.path.exists(location):
      return location
  
  # Check HOME directory locations second
  _home = os.getenv('HOME')
  if _home is not None:
    home_locations = [
      os.path.join(_home, 'coaia.json'),
      os.path.join(_home, '.config', 'jgwill', 'coaia.json'),
      os.path.join(_home, 'Documents', 'coaia.json')
    ]
    for location in home_locations:
      if os.path.exists(location):
        return location
  
  # Finally check other relative paths
  other_locations = [
    '../../shared/etc/coaia.json',
    '../shared/etc/coaia.json',
    '../../etc/coaia.json',
    '../etc/coaia.json',
    '../coaia.json',
    '../config/coaia.json',
    './etc/coaia.json'
  ]

  for location in other_locations:
    if os.path.exists(location):
      return location

  return None

def load_env_file(env_path='.env'):
    """Simple .env file loader compatible with Python 3.6

    Loads environment variables from .env file and sets them in os.environ.
    Local .env file takes precedence over pre-existing environment variables.
    """
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                lines_read = 0
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove surrounding quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        env_vars[key] = value
                        # Always set in os.environ - local .env takes precedence
                        os.environ[key] = value
                        lines_read += 1
        except Exception as e:
            print(f"Warning: Error loading .env file from '{env_path}': {e}")
    else:
        # Only warn about missing custom .env paths, not the default .env
        if env_path != '.env':
            print(f"Warning: Custom .env file not found: {env_path}")
    return env_vars

def merge_configs(base_config, override_config):
    """Deep merge two configuration dictionaries"""
    merged = base_config.copy()
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged

def read_config(env_path=None):
    global config
    global _loaded_env_path

    # Determine .env path: explicit param > COAIAPY_ENV_PATH env var > default .env
    if env_path is None:
        env_path = os.getenv('COAIAPY_ENV_PATH', '.env')

    # Reload config if env_path changed or config not loaded yet
    if config is None or _loaded_env_path != env_path:
        # Load .env file first if it exists
        env_vars = load_env_file(env_path)
        if not env_vars and env_path != '.env':
            # Warn if custom env_path was specified but file not found
            print(f"Warning: COAIAPY_ENV_PATH={env_path} was specified but file not found or empty")
        
        # Default configuration
        config = {
            "jtaleconf": {
                "host": "localhost",
                "port": 6379,
                "password": "",
                "ssl": False
            },
            "openai_api_key": "",
            "pollyconf": {"key": "", "secret": "", "region": "us-east-1"}
        }
        
        # Load HOME config first (base configuration)
        _home = os.getenv('HOME')
        if _home is not None:
            home_config_path = os.path.join(_home, 'coaia.json')
            if os.path.exists(home_config_path):
                try:
                    with open(home_config_path) as config_file:
                        home_config = json.load(config_file)
                        config = merge_configs(config, home_config)
                except Exception as e:
                    print(f"Warning: Error loading HOME config: {e}")
        
        # Load current directory config for overrides
        current_config_path = './coaia.json'
        if os.path.exists(current_config_path):
            try:
                with open(current_config_path) as config_file:
                    current_config = json.load(config_file)
                    config = merge_configs(config, current_config)
            except Exception as e:
                print(f"Warning: Error loading current directory config: {e}")
        
        # If no configs found, try find_existing_config for backward compatibility
        if not os.path.exists(os.path.join(_home, 'coaia.json') if _home else '') and not os.path.exists('./coaia.json'):
            _cnf = find_existing_config()
            if _cnf and os.path.exists(_cnf):
                try:
                    with open(_cnf) as config_file:
                        fallback_config = json.load(config_file)
                        config = merge_configs(config, fallback_config)
                except Exception as e:
                    print(f"Warning: Error loading fallback config: {e}")

        # Helper function to get value from system env first, then .env, then config
        def get_env_value(env_key, config_value, env_vars_dict=None):
            if env_vars_dict is None:
                env_vars_dict = env_vars
            return os.getenv(env_key) or env_vars_dict.get(env_key) or config_value
        
        # Check for placeholder values and replace with environment variables if needed
        config["openai_api_key"] = get_env_value("OPENAI_API_KEY", config["openai_api_key"])
        config["pollyconf"]["key"] = get_env_value("AWS_KEY_ID", config["pollyconf"]["key"])
        config["pollyconf"]["secret"] = get_env_value("AWS_SECRET_KEY", config["pollyconf"]["secret"])
        config["pollyconf"]["region"] = get_env_value("AWS_REGION", config["pollyconf"]["region"])
        
        # Redis/Upstash configuration with priority order:
        # 1. UPSTASH_REDIS_REST_URL/TOKEN (Upstash direct)
        # 2. KV_REST_API_URL/TOKEN (Vercel)
        # 3. KV_URL or REDIS_URL (Vercel connection strings)
        # 4. REDIS_HOST/PASSWORD (traditional)
        # 5. Config files
        
        # Check for REST API format first (HTTPS URLs)
        upstash_rest_url = (get_env_value("UPSTASH_REDIS_REST_URL", "") or
                            get_env_value("KV_REST_API_URL", ""))
        upstash_rest_token = (get_env_value("UPSTASH_REDIS_REST_TOKEN", "") or
                              get_env_value("KV_REST_API_TOKEN", ""))
        
        # Check for Redis connection string format (redis:// or rediss://)
        redis_connection_url = (get_env_value("KV_URL", "") or
                               get_env_value("REDIS_URL", ""))
        
        if upstash_rest_url:
            # Parse Upstash REST URL to extract host, port, and SSL settings
            try:
                parsed_url = urlparse(upstash_rest_url)
                config["jtaleconf"]["host"] = parsed_url.hostname or config["jtaleconf"]["host"]
                # Upstash typically uses port 6379 for TLS connections
                config["jtaleconf"]["port"] = parsed_url.port if parsed_url.port else 6379
                # Enable SSL if the scheme is https
                config["jtaleconf"]["ssl"] = (parsed_url.scheme == 'https')
                # Use the REST token as password if available
                if upstash_rest_token:
                    config["jtaleconf"]["password"] = upstash_rest_token
            except Exception as e:
                print(f"Warning: Error parsing REST API URL: {e}")
        elif redis_connection_url:
            # Parse Redis connection string (redis://[user:password@]host[:port][/database])
            try:
                parsed_url = urlparse(redis_connection_url)
                config["jtaleconf"]["host"] = parsed_url.hostname or config["jtaleconf"]["host"]
                config["jtaleconf"]["port"] = parsed_url.port if parsed_url.port else 6379
                # rediss:// uses SSL, redis:// does not
                config["jtaleconf"]["ssl"] = (parsed_url.scheme == 'rediss')
                # Extract password from URL
                if parsed_url.password:
                    config["jtaleconf"]["password"] = parsed_url.password
            except Exception as e:
                print(f"Warning: Error parsing Redis connection URL: {e}")
        else:
            # Fallback to traditional Redis environment variables
            # Try REDIS_HOST first, then fall back to UPSTASH_HOST if REDIS_HOST not set
            redis_host = get_env_value("REDIS_HOST", "")
            if redis_host:
                config["jtaleconf"]["host"] = redis_host
            else:
                config["jtaleconf"]["host"] = get_env_value("UPSTASH_HOST", config["jtaleconf"]["host"])

            config["jtaleconf"]["port"] = int(get_env_value("REDIS_PORT", config["jtaleconf"]["port"]))
            
            # Try REDIS_PASSWORD first, then fall back to UPSTASH_PASSWORD if REDIS_PASSWORD not set
            redis_password = get_env_value("REDIS_PASSWORD", "")
            if redis_password:
                config["jtaleconf"]["password"] = redis_password
            else:
                config["jtaleconf"]["password"] = get_env_value("UPSTASH_PASSWORD", config["jtaleconf"]["password"])
        
        # Add Langfuse environment variable support
        config["langfuse_secret_key"] = get_env_value("LANGFUSE_SECRET_KEY", config.get("langfuse_secret_key", ""))
        config["langfuse_public_key"] = get_env_value("LANGFUSE_PUBLIC_KEY", config.get("langfuse_public_key", ""))
        config["langfuse_base_url"] = get_env_value("LANGFUSE_HOST", config.get("langfuse_base_url", "https://us.cloud.langfuse.com"))
        config["langfuse_auth3"] = get_env_value("LANGFUSE_AUTH3", config.get("langfuse_auth3", ""))

        # Track which env_path was used to load this config
        _loaded_env_path = env_path

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
    # Read OpenAI API key from coaia.json
    
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
    
  system_instruction = config.get('d2s_instruction', 'You do : Receive a text that requires to put details into shapes. you group elements of different nature and summarize them. REMEMBER: Dont introduce nor conclude, just output results. No comments.') 
  
  
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
        'Authorization': f"Bearer {openai_api_key}",
        'Content-Type': "application/json"
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
def _newjtaler(jtalecnf, verbose=False):
  try:
    if verbose:
        print(f"Connecting to Redis server:")
        print(f"  Host: {jtalecnf.get('host', 'N/A')}")
        print(f"  Port: {jtalecnf.get('port', 'N/A')}")
        print(f"  SSL: {jtalecnf.get('ssl', 'N/A')}")
        # Mask password for security - only show last 4 characters
        password = jtalecnf.get('password', '')
        if password:
            # Show last 4 chars, but handle short passwords safely
            masked = '***' + password[-4:] if len(password) >= 4 else '***'
            print(f"  Password: {masked}")  # nosec - password is masked before logging
        else:
            print(f"  Password: (empty)")
    
    _r = redis.Redis(
    host=jtalecnf['host'],
    port=int(jtalecnf['port']),
    password=jtalecnf['password'],  # nosec - password needed for authentication
    ssl=jtalecnf['ssl'])
    
    if verbose:
        print("  Status: Connection established successfully")
    
    return _r
  except Exception as e :
    print(f"Error connecting to Redis: {e}")
    print(f"Redis configuration: host={jtalecnf.get('host', 'N/A')}, port={jtalecnf.get('port', 'N/A')}, ssl={jtalecnf.get('ssl', 'N/A')}")
    print("Troubleshooting tips:")
    print("  1. Set Redis credentials via environment variables:")
    print("     - Upstash: UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN")
    print("     - Vercel: KV_REST_API_URL and KV_REST_API_TOKEN (or KV_URL/REDIS_URL)")
    print("  2. Check .env file in current directory for these variables")
    print("  3. Verify credentials in ./coaia.json or ~/coaia.json (jtaleconf section)")
    print("  4. Ensure network connectivity to Redis/Upstash instance")
    print("  5. Use --verbose flag to see detailed connection information")
    return None

def _taleadd(_r:redis.Redis,k:str,c:str,quiet=False,ttl=None):
  try:
    if ttl:
      _r.set(k, c, ex=ttl)
    else:
      _r.set(k, c)
    _kv=_r.get(k)
    if not quiet:
      print(_kv)
    return _kv
  except Exception as e :
    print(e)
    return None

def tash(k:str,v:str,ttl=None,quiet=True,verbose=False):
  
  _r=None
  try:
    #from coaiamodule import read_config
    jtalecnf=read_config()['jtaleconf']
    _r=_newjtaler(jtalecnf, verbose=verbose)
  except Exception as e:
    print(e)
    print('init error')
    return None
  if _r is not None:
    ttl_seconds = ttl * 60 if ttl > 0 else None
    result=_taleadd(_r,k,v,quiet,ttl_seconds)
    if result is not None:
      if not quiet: print('Stashed success:'+k)
    else:
      if not quiet: print('Stashing failed')
    return result

def fetch_key_val(key, output_file=None, verbose=False):
    try:
        jtalecnf = read_config()['jtaleconf']
        _r = _newjtaler(jtalecnf, verbose=verbose)
        if _r is None:
            print("Error: Redis connection failed.")
            print("Note: Detailed connection error information printed above.")
            sys.exit(2)
        value = _r.get(key)
        if value is None:
            print(f"Error: Key '{key}' not found in Redis memory.")
            sys.exit(1)
        value = value.decode('utf-8')
        if output_file:
            with open(output_file, 'w') as file:
                file.write(value)
            print(f"Key: {key}  fetched and saved to {output_file}")
        else:
            print(value)
    except redis.ConnectionError as e:
        print(f"Error: Redis connection failed - {e}")
        print("Please check your Redis/Upstash configuration.")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def initial_setup():
    sample_config = {
        "username": "SSH_USER",
        "user_id": "USER_ID",
        "openai_api_key": "__API_KEY__",
        "model": "gpt-4o-mini",
        "model2": "gpt-3.5-turbo",
        "pollyconf": {
            "key": "__AWS_KEY_ID__",
            "secret": "__AWS_SECRET_KEY__",
            "region": "us-east-1"
        },
        "dalle_api_endpoint": "https://api.openai.com/v1/images/generations",
        "pyapp_dalle_api_2405": "__API_KEY__",
        "default_size": "1024x1024",
        "openai_api_url": "https://api.openai.com/v1/chat/completions",
        "openai_transcription_api_url": "https://api.openai.com/v1/audio/transcriptions",
        "default_temperature": 0.35,
        "default_preprompt_instruction": "",
        "default_preprompt_instruction1": "consider these instructions before what to do:  'Creativity is not a requirement for creating.  Creating is an orientation and creativity is different and relate to the character traits of someone.  Many professionals who studied creators are just not capable to comprehend that the creativity of someone will not make she/he, a creator.  If anything, the capacity of that character traits will deform itself into defect of character when in reaction to past, present or future circumstances.  Hardly said, if you describe yourself as having creativity in your character, mastering your creative process will demand you more work to unbuilt what you learned in the traditional learning system.  Our traditional learning system does not educate us in order to become masters of our own creative process, rather,  education is teaching us to give the correct responses to circumstances.  That in itself is enough for creativity for a tragic unfolding of neuronal connections that are just not part of the creative process but a mental database of constructs making you better in responding, limiting your potential for creating what you want.'  Prompt: ",
        "d2s_default_temperature": 0.25,
        "d2s_temperature": 0.25,
        "d2s_instruction": "You do : Receive a text that requires to put details into shapes. you group elements of different nature and summarize them. REMEMBER: Dont introduce nor conclude, just output results. No comments.",
        "dictkore_default_temperature": 0.2,
        "dictkore_temperature": 0.2,
        "dictkore_instruction": "You do : Receive a dictated text that requires correction and clarification.\n\n# Corrections\n\n- In the dictated text, spoken corrections are made. You make them and remove the text related to that to keep the essence of what is discussed.\n\n# Output\n\n- You keep all the essence of the text (same length).\n- You keep the same style.\n- You ensure annotated dictation errors in the text are fixed.",
        "stcrev_instruction": "you generate a new version from the received review and corrections using the original text supplied",
        "stcrev_pre_prompt": "consider review and correct bellow to generate a new version of the original text:\n\n## Review and corrections:\n\n\n\"\"\"",
        "stcrev_temperature": 0.25,
        "stcrev_default_temperature": 0.25,
        "csv2json_instruction": "transform this CSV content into json (encapsulate output and don't comment it) :",
        "csv2json_temperature": 0.35,
        "summarizer_instruction": "You Summarize the content bellow in its native language with coherence and integrity even if the summary is longer.",
        "summarizer_temperature": 0.2,
        "faction_instruction": "from the supplied input you create a clear list of actions with their description after their title. You output just that list. REMEMBER: Dont introduce nor conclude, just output results. No comments.",
        "faction_temperature": 0.11,
        "contentreducer_instruction": "you reduce the amount of characters in the following text without changing the notions (you can get rid of what the teachers says that are irrelevant to the core understanding).  simply output the resulting generated text. REMEMBER: Dont introduce nor conclude, just output results. No comments.",
        "contentreducer_temperature": 0.2,
        "stcmasterywrap_instruction": "you are wrapping with sufficient details the input content which is part of something we want to master.  REMEMBER: Dont introduce nor conclude, just output results. No comments.",
        "stcmasterywrap_temperature": 0.2,
        "nutrifact_instruction": "extract and clean nutritional value from text extracted from image bellow and output as structured data in json  format '{per_nb_grams: X, nutrition_facts: {...}}' (no comments, just outputs): ",
        "nutrifact_temperature": 0.2,
        "mkfn_instruction": "you are an assistant in making a safe file naming  from the input text.  Maximum 24 characters, underscore and 'CaML' markup.  No extension, just a 'basename'.  Clean out any irrelevant content from the input  .  (just output result, no comments )",
        "mktn_temperature": 0.2,
        "compact_temperature": 0.2,
        "compact_instruction": "You compact the input text bellow to the lowest amout of content to keep its essence and have an overview of what it speaks in the original input language. (just output result, no comments )",
        "ca_instruction": "you are a useful assistant using the creative process.(just output results, no comments):",
        "ca_temperature": 0.3,
        "ca_mns": "coaia",
        "mns": {
            "ocoaia": "ft:gpt-4o-mini-2024-07-18:jgwill:coaia240822b:9zDtl5Dq",
            "coaia": "ft:gpt-4o-2024-08-06:jgwill:coaia240830d:A1vOInwF",
            "tht": "ft:gpt-3.5-turbo-1106:jgwill:tht240904g:A3sF4S2j"
        },
        "jtaleconf": {
            "host": "adapting-hyena-26846.upstash.io",
            "port": 6379,
            "password": "__UPSTASH_PASSWORD__",
            "ssl": True,
            "notes": "it is using the upstash service not the redis cloud for which I dont yet see the differences."
        }
    }
    home = os.getenv('HOME')
    config_path = os.path.join(home, 'coaia.json')
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump(sample_config, config_file, indent=4)
        print(f"Sample config created at {config_path}")
    else:
        print(f"Config already exists at {config_path}")

