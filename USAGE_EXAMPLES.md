# Score Configuration Apply Functionality - Usage Examples

This document demonstrates the new score-configs apply functionality with comprehensive value validation.

## New CLI Commands

### 1. Apply Score Configuration

Apply a score configuration to traces or sessions with automatic validation:

```bash
# Apply to a trace
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "Very Helpful"
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value 4

# Apply to a session
coaia fuse score-configs apply "Quality Check" --session-id xyz789 --value true
coaia fuse score-configs apply "Quality Check" --session-id xyz789 --value "yes"

# Apply to trace with observation and comment
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --observation-id obs456 --value 8.5 --comment "High accuracy result"

# Using config ID instead of name
coaia fuse score-configs apply --config-id cfg-123 --session-id xyz789 --value false
```

### 2. List Available Configurations

```bash
# List all available configs
coaia fuse score-configs available

# Filter by category
coaia fuse score-configs available --category narrative

# Show only cached configs (faster)
coaia fuse score-configs available --cached-only

# JSON output
coaia fuse score-configs available --json
```

### 3. Show Configuration Details

```bash
# Show basic config info
coaia fuse score-configs show "Helpfulness"

# Show with validation requirements
coaia fuse score-configs show "Helpfulness" --requirements

# JSON output
coaia fuse score-configs show "Accuracy Score" --json
```

### 4. Enhanced Scores Apply (now supports sessions)

```bash
# Apply score to trace
coaia fuse scores apply --trace-id abc123 --name "Custom Score" --value 7.5

# Apply score to session
coaia fuse scores apply --session-id xyz789 --score-id score-123 --value 8.0 --comment "Good performance"

# Apply to specific observation
coaia fuse scores apply --trace-id abc123 --observation-id obs456 --name "Quality" --value 9.0
```

## Validation Examples

### Boolean Score Validation

```bash
# These will work:
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value true
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value "false"
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value 1
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value "yes"
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value "off"

# This will fail with helpful error:
coaia fuse score-configs apply "Pass/Fail" --trace-id abc123 --value "maybe"
# Error: Invalid boolean value 'maybe'. Use true/false, 1/0, yes/no, or on/off
```

### Categorical Score Validation

```bash
# These will work (by value):
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value 4
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "3"

# These will work (by label, case-insensitive):
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "Very Helpful"
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "helpful"
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "NOT HELPFUL"

# This will fail with helpful error showing valid options:
coaia fuse score-configs apply "Helpfulness" --trace-id abc123 --value "amazing"
# Error: Invalid categorical value 'amazing'. Valid options: 'Not Helpful' (1), 'Somewhat Helpful' (2), 'Helpful' (3), 'Very Helpful' (4), 'Extremely Helpful' (5)
```

### Numeric Score Validation

```bash
# These will work (within range 0.0-10.0):
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value 5.5
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value "8"
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value 0.0
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value "10.0"

# These will fail with range information:
coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value -1
# Error: Value -1.0 is below minimum. Valid range: 0.0 to 10.0

coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value 15
# Error: Value 15.0 is above maximum. Valid range: 0.0 to 10.0

coaia fuse score-configs apply "Accuracy Score" --trace-id abc123 --value "not-a-number"
# Error: Invalid numeric value 'not-a-number'. Must be a number
```

## Smart Caching Features

The system uses smart caching to optimize performance:

1. **Cache-first retrieval**: Checks project cache before API calls
2. **Auto-refresh**: Refreshes stale cache entries automatically  
3. **Cache management**: Updates cache after successful API calls
4. **Project-aware**: Maintains separate cache per Langfuse project

## Error Handling

Comprehensive error messages help users understand validation requirements:

- **Config not found**: Clear message when configuration doesn't exist
- **Validation errors**: Detailed explanation of why value was rejected
- **Target validation**: Ensures exactly one of trace-id or session-id is specified
- **Type-specific guidance**: Shows valid options for categorical, range for numeric, formats for boolean

## Integration with Existing Systems

- **Seamless integration**: Uses existing `create_score_for_target()` function
- **Backward compatibility**: All existing score commands continue to work
- **Enhanced functionality**: Existing `scores apply` now supports sessions
- **Consistent patterns**: Follows established CLI argument patterns

## Performance Benefits

- **Smart caching**: Reduces API calls through intelligent caching
- **Batch operations**: Cache warming reduces latency for multiple operations  
- **Local validation**: Client-side validation prevents unnecessary API calls
- **Efficient lookups**: Name-to-ID resolution cached locally

## Use Cases

1. **Interactive scoring**: Quick manual scoring with validation feedback
2. **Automated workflows**: Script-based scoring with error handling
3. **Batch processing**: Apply multiple scores efficiently using cached configs
4. **Quality assurance**: Validate score values before submission
5. **Team collaboration**: Share and reuse score configurations consistently