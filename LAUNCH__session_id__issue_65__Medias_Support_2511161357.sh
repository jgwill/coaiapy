. _env.sh
export session_id__parent_jgwill_Miadi_STCMastery_Claude_Agent_SDK_and_PR87_2510311507
export session_id__issue_65__Medias_Support_2511161357

claude " in @references/openapi.json you will find the media endpoints (operations) we will want both @coaiapy/cofuse.py and the WHOLE CLI wrapper exposed in @pyproject.yaml and the @coaiapy-mcp/ to support the medias operations.  we will also need to make sure that we have clear testing for that, the @tests/.env has both Langfuse and redis environment for you to prepare adequate testing ground.
@tests/image_medias.txt @tests/dropbox_shared.txt are potential medias URL to embed or something, I never achived to make this working so...  there is also : tests/notebook_graph.jpg that I dont know if we can upload a jpg to langfuse, you will investigate that.

the ./references/ has other files that might help you.

Analyze first before you prepare your plan.

You might also plan at how this will fits in the 'coaia pipeline' subcommands as we might be adding medias somehow in a sequence of action that are part of the pipeline.

ADDITIONAL INFO:

the tests/dropbox_shared.txt was created with the CLI command 'droxul' using 'droxul upload <file.jpg> /<derired_full_path_on_dropbox>' then 'droxul share <derired_full_path_on_dropbox>' which outputs that shared URL which we will want to know if they can be use within a Trace where we probably add a media somewhere in the trace, I dont know if that is in an observation or if that it has its own media entity, you will make this happen and known.  

You will add a new trace using the 'coaiapy_aetherial' (that uses this very tool that you are working on) and in the Input is the context, my request etc and you will hopefully Patch the trace 'Output' at the end and during your process, you will add Observations to that trace_id : $session_id__issue_65__Medias_Support_2511161357 within the session_id : $session_id__parent_jgwill_Miadi_STCMastery_Claude_Agent_SDK_and_PR87_2510311507

" \
	--session-id ${session_id__issue_65__Medias_Support_2511161357} \
	--mcp-config /src/.mcp.coaiapy.env.aetherial.json /src/.mcp.github.json \
	--permission-mode plan

