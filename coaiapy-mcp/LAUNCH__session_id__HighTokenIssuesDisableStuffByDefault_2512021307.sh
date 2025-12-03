#!/bin/bash
. _env.sh
export SESSION_ID=7110c4c2-d551-4ed7-9b8b-5907647f0689
export session_id__HighTokenIssuesDisableStuffByDefault_2512021307
export session_id__HighTokenIssuesDisableStuffByDefault_2512021307__MCP_CONFIG
export session_id__HighTokenIssuesDisableStuffByDefault_2512021307__ADD_DIR
claude "using this MCP has a high tokens count, by default, we would disable some of the tools that we dont need - looking at prompts, I never really used any of them by default, I dont know which other tools/resources/prompts that are taking that much tokens in the context when we load that MCP.  We would add an environment variable that enable us to select what we want to activate in the MCP (by semantic grouping of desired tools or something meaningful) and by default we would have something like STANDARD and that variable could have FULL or separated sets of features" --mcp-config $session_id__HighTokenIssuesDisableStuffByDefault_2512021307__MCP_CONFIG --add-dir $session_id__HighTokenIssuesDisableStuffByDefault_2512021307__ADD_DIR --session-id $session_id__HighTokenIssuesDisableStuffByDefault_2512021307 
#--permission-mode plan
