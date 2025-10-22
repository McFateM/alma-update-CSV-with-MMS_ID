# Alma CSV Updater - Usage Guide

This guide provides detailed instructions for using the Alma CSV Updater application.

## Table of Contents

1. [Starting the Application](#starting-the-application)
2. [Using the Interface](#using-the-interface)
3. [Understanding the Results](#understanding-the-results)
4. [Working with Logs](#working-with-logs)
5. [Common Scenarios](#common-scenarios)
6. [Best Practices](#best-practices)

## Getting Started

### Launch the Application

Run the application using one of the provided launch scripts:

**macOS/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

### Interface Overview

The application window displays:
- **Display WORKFLOW Instructions**: Button to view workflow documentation in a popup
- **Select CSV to Update**: Button to choose your CSV file for processing
- **Selected CSV path**: Full path to your chosen file (displayed after selection)
- **Reference CSV path**: Full path to the Alma reference data on the network
- **Process CSV**: Button to begin the update operation
- **Status messages**: Green text showing successful operations
- **Warnings**: Red text highlighting issues that need attention
- **Results**: Detailed information about the processing outcome

The window is scrollable to accommodate long processing results.

## Using the Interface

### Step 1: Verify Reference CSV Path

When the application starts, you'll see the reference CSV path displayed at the top in gray text:
```
Reference CSV: /Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv
```

This confirms the application can access the network reference file.

### Step-by-Step Process

1. **View Workflow (Optional)**: Click "Display WORKFLOW Instructions" to review the workflow documentation
2. **Select Your CSV**: Click "Select CSV to Update" and choose your file
   - The full path to your selected file will be displayed
3. **Verify Reference Path**: Confirm the reference CSV path is correct
   - Default: `/Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`
4. **Process**: Click "Process CSV" to begin updating
5. **Review Results**: Check the green status messages and any red warnings
6. **Locate Updated File**: Find your updated CSV in the same directory as the original
   - Original: `Photos_For_DG.csv` (unchanged)
   - Updated: `UPDATED_Photos_For_DG.csv` (newly created)

### Step 3: Process the File

1. Click the **"Process and Update"** button
2. Watch the progress messages as the application:
   - Loads the reference CSV from the network share
   - Removes any completely blank rows from your CSV
   - Creates a lookup index
   - Processes each non-blank row in your CSV
   - Updates empty `mms_id` cells
   - Saves the changes

### Step 4: Review the Results

The application displays results in two areas:

**Green Status Message (Main Results):**
- Number of blank rows removed (if any)
- Total rows processed (excludes blank rows)
- Number of rows updated successfully
- Number of rows skipped (already had MMS IDs)
- Counts of not-found and ambiguous matches
- Full path where the updated CSV was saved

**Red Warning Message (If Applicable):**
- Details of `originating_system_id` values not found in reference
- Details of multiple/ambiguous matches
- Shows sample entries for each issue

## Understanding the Results

### Success Cases

**Row Updated:**
- The `originating_system_id` was found exactly once in the reference CSV
- The corresponding MMS ID was written to the `mms_id` column
- Example: `dg_1751378367` → `991011688282104641`

**Row Skipped:**
- The `mms_id` column already contained a valid MMS ID
- The row was left unchanged

**Blank Row Removed:**
- Completely empty rows (all columns blank) are automatically removed
- Does not count toward any statistics
- Keeps the CSV file clean

### Warning Cases

**Not Found in Reference:**
- The `originating_system_id` doesn't exist in the reference CSV
- The `mms_id` cell is marked with: `NOT FOUND IN ALMA - YYYY-MM-DD HH:MM:SS`
- This row will be re-processed on subsequent runs
- Check the red warning message for the specific ID values

**Multiple Matches (Ambiguous):**
- The `originating_system_id` was found in multiple Network Numbers
- The row is not updated (ambiguous match)
- Check logs for details on which Network Numbers contained the ID

## Working with Logs

### Log Location

Logs are saved in the `logs/` directory with timestamped filenames:
```
logs/alma_csv_updater_20251022_140037.log
```

### Log Contents

Each log file contains:
- Application start time and log file path
- Reference CSV path and loading details
- File selection events (with full paths)
- Number of blank rows removed (if any)
- Reference CSV loading details (path, row count, sample entries)
- Processing progress
- **WARNING**: Specific rows not found or with multiple matches
- Final summary statistics
- Any errors encountered

### Reading Logs

**To find not-found entries:**
```bash
grep "WARNING.*No match found" logs/alma_csv_updater_*.log
```

**To find multiple matches:**
```bash
grep "WARNING.*Multiple matches" logs/alma_csv_updater_*.log
```

**To view the latest log:**
```bash
tail -f logs/alma_csv_updater_*.log | tail -100
```

## Common Scenarios

### Scenario 1: First-Time Processing

**Situation:** You have a new CSV with empty `mms_id` columns and possibly some blank rows.

**Steps:**
1. Start the application
2. Verify the reference CSV path shown at the top
3. Select your CSV file (full path will be displayed)
4. Click "Process and Update"
5. Review results:
   - Note if any blank rows were removed
   - Green message shows how many were updated
   - Red warnings show any not-found entries
6. Find your updated file with the UPDATED_ prefix in the same directory as the original

### Scenario 2: Re-Processing After Reference Update

**Situation:** Some IDs were marked "NOT FOUND IN ALMA", but they've since been added to the reference CSV.

**Steps:**
1. Start the application
2. Select the UPDATED_ CSV file from the previous run (or your original if you want to start fresh)
3. Click "Process and Update"
4. The app recognizes "NOT FOUND IN ALMA" entries as empty
5. It attempts to find MMS IDs again
6. Successfully found entries are updated with real MMS IDs
7. A new UPDATED_ file is created (or overwrites the previous UPDATED_ file if you selected it)

### Scenario 3: Partial Update

**Situation:** Your CSV has some MMS IDs filled, some empty, and some trailing blank rows.

**Steps:**
1. The app automatically skips rows with existing MMS IDs
2. Blank rows are removed automatically
3. Only empty or "NOT FOUND IN ALMA" entries are processed
4. Review the "Skipped" and "Removed" counts to see the breakdown

### Scenario 4: Investigating Warnings

**Situation:** You have warnings in red about not-found entries.

**Steps:**
1. Note the sample IDs shown in the red warning message
2. Open the corresponding log file (path shown at startup)
3. Search for "WARNING" to see all problematic entries
4. Verify these IDs exist (or should exist) in the reference CSV at:
   `/Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`

## Best Practices

### Before Processing

1. **Backup Your CSV**: The app preserves your original, but keep additional backups for important data
2. **Verify Network Mount**: Ensure `/Volumes/MEDIADB/` is accessible
3. **Check Reference Path**: Verify the path shown in the app UI is correct
4. **Check CSV Format**: Confirm your CSV has the required columns
5. **Clean Up Manual Edits**: Remove any intentional blank rows if they're not needed

### During Processing

1. **Watch Progress**: Monitor the progress messages for any immediate issues
2. **Don't Close Early**: Wait for "Processing complete!" message
3. **Note the Log Path**: Shown at startup for later reference

### After Processing

1. **Review Results**: Check both green and red messages
2. **Note File Paths**: The full paths for both original and UPDATED_ files are shown
3. **Check Blank Row Count**: Note if any were removed
4. **Examine Warnings**: Investigate any not-found or ambiguous entries
5. **Verify Updates**: Open the UPDATED_ file and spot-check a few rows
6. **Save Logs**: Keep log files for audit trails and troubleshooting
7. **Use the UPDATED_ File**: The original file is preserved unchanged

### For Not-Found Entries

1. **Check Reference**: Verify the ID exists in the reference CSV
2. **Wait for Updates**: If IDs are being added to reference, re-run later
3. **Document Issues**: Note which IDs consistently fail to match
4. **Investigate Format**: Ensure ID formats match between files

### Regular Maintenance

1. **Clean Old Logs**: Periodically remove old log files from `logs/` directory
2. **Update Reference**: Ensure the network reference CSV is current
3. **Test Changes**: After any modifications, test with a small sample CSV first
4. **Manage UPDATED_ Files**: Keep track of which version you're working with

## Troubleshooting Tips

**Problem:** "Reference CSV not found" error
- **Solution:** Check that `/Volumes/MEDIADB/` is mounted and accessible
- **Verification:** The reference path is shown at the top of the app window

**Problem:** All rows show "Not found in reference"
- **Solution:** Verify the column names in both CSVs match expected format

**Problem:** Application window is too small to see all messages
- **Solution:** The window has scrolling enabled - scroll down to see all content

**Problem:** Can't tell which specific IDs failed
- **Solution:** Check the red warning message for samples, or open the log file for complete details

**Problem:** CSV has many blank rows at the end
- **Solution:** These are automatically removed during processing - no action needed

**Problem:** File paths are truncated in the UI
- **Solution:** Hover over the text or check the log file for full paths

---

For additional help or to report issues, consult the logs or contact the system administrator.
