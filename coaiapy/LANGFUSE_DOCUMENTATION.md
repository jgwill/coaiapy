# Langfuse Integration

- Added a new Python module `cofuse.py` to handle Langfuse HTTP requests using `requests`.
- Provided commands in `coaiacli.py` under `fuse` subparser to manage:
  - Comments
  - Prompts
  - Datasets
  - Sessions (create a root trace and add child nodes)
- Utilizes `read_config()` from `coaiamodule` for authentication details.
- Exposes:
  - `create_session(session_id, user_id, session_name)`  
  - `add_trace_node(session_id, trace_id, user_id, node_name)`
  - `list_prompts()`, `get_prompt(...)`, `create_prompt(...)`
  - `list_datasets()`, `get_dataset(...)`, `create_dataset(...)`
  - `get_comments()`, `post_comment(...)`

## Usage

### comments
• List comments:
  coaia fuse comments list  
• Post a new comment:
  coaia fuse comments post "Your comment here"

### prompts
• List prompts (all pages):
  coaia fuse prompts list
• Get a specific prompt:
  coaia fuse prompts get myPrompt  
• Create a prompt:
  coaia fuse prompts create myPrompt "Prompt text"

### datasets
• List datasets:
  coaia fuse datasets list  
• Get a dataset:
  coaia fuse datasets get myDataset  
• Create a dataset:
  coaia fuse datasets create myDataset

### sessions
• Create a new session:
  coaia fuse sessions create session123 userABC -n "My Session" -f mysession.yml  
• Add a child node:
  coaia fuse sessions addnode session123 trace01 userABC -n "First Node" -f mysession.yml  
• View session file:
  coaia fuse sessions view -f mysession.yml

### scores (alias: sc)
• Create a new score:
  coaia fuse scores create myScoreId -n "Score Name" -v 1.5  
• Apply a score to a trace:
  coaia fuse scores apply someTrace myScoreId -v 2.0