# Sample CSV Files for Testing

This directory contains sample CSV files for testing the Alma CSV Updater application.

## Files

### sample_input.csv
A sample input CSV file with the required columns that needs MMS ID updates.

### sample_reference.csv
A sample reference CSV file mimicking the structure of the network file.

## How to Test

1. Copy `sample_reference.csv` to `/tmp/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv` to use the local fallback:
   ```bash
   # On Linux/Mac
   cp samples/sample_reference.csv /tmp/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv
   
   # On Windows (in Command Prompt)
   copy samples\sample_reference.csv C:\temp\All-Digital-Items-MMS_ID-with-File-Internal-Path.csv
   ```

2. Run the application:
   ```bash
   ./run.sh  # or run.bat on Windows
   ```

3. Click "Select CSV File" and choose `samples/sample_input.csv`

4. Click "Process and Update"

5. Review the updated `samples/sample_input.csv` file to see the results.

## Expected Results

The sample_input.csv should be updated with MMS IDs from the reference file for all rows that:
- Have an empty `mms_id` field
- Have a valid `originating_system_id` field
- Match a "Network Number" in the reference file
