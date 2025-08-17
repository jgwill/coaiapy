#!/bin/bash
# Demo pipeline workflow using coaia observations

# Step 1: Create trace and export environment
echo '=== Creating trace ==='
eval $(coaia fuse traces create $(uuidgen) -s $(uuidgen) -u pipeline-user -n 'Demo Pipeline' --export-env)

# Step 2: Create main SPAN observation 
echo '=== Creating main SPAN ==='
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -t SPAN -n 'Main Processing' --export-env)
main_span=$COAIA_LAST_OBSERVATION_ID

# Step 3: Add child observations under the SPAN
echo '=== Adding child observations ==='
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -n 'Data Loading' --parent $main_span --export-env)
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -n 'Data Processing' --parent $main_span --export-env)  
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -n 'Results Export' --parent $main_span --export-env)

echo '=== Pipeline complete ==='
echo "Trace ID: $COAIA_TRACE_ID"
echo "Last observation: $COAIA_LAST_OBSERVATION_ID"

