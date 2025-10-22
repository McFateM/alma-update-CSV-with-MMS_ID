# alma-update-CSV-with-MMS_ID

A Flet/Python desktop application to update the `mms_id` column of a selected CSV file using information gathered from the network reference CSV file at `/Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`.

## Features

- **Simple GUI**: Single-page Flet interface for easy file selection and processing
- **Workflow Instructions**: Built-in button to display workflow documentation
- **Full Path Display**: Shows complete file paths for both selected and reference CSV files
- **CSV Processing**: Opens and processes local CSV files, automatically removing blank rows
- **Safe File Handling**: Saves updated CSV with "UPDATED_" prefix, preserving original file
- **Network Integration**: Accesses reference data from mounted network volume
- **Intelligent Matching**: Uses substring matching to find `originating_system_id` within "Network Number"
- **Smart Updates**: Only updates rows with empty `mms_id` and valid `originating_system_id`
- **Not Found Marking**: Marks rows not found in reference with timestamped "NOT FOUND IN ALMA" entries
- **Blank Row Removal**: Automatically removes completely blank rows during processing
- **Progress Tracking**: Visual feedback with scrollable interface during processing
- **Comprehensive Logging**: File and console logging with timestamps for all operations
- **Warning Detection**: Red-highlighted warnings for not-found and ambiguous matches
- **Error Handling**: Comprehensive error handling and user feedback

## Requirements

- Python 3.8 or higher
- macOS with network share mounted at `/Volumes/MEDIADB/`
- Required Python packages: `flet`, `pandas`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/McFateM/alma-update-CSV-with-MMS_ID.git
   cd alma-update-CSV-with-MMS_ID
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start (Recommended)

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```cmd
run.bat
```

These scripts will automatically:
- Create a virtual environment if needed
- Install dependencies
- Launch the application

For detailed usage instructions, see [USAGE.md](USAGE.md).

For workflow guidance, click the "Display WORKFLOW Instructions" button in the app or see [WORKFLOW.md](WORKFLOW.md).

## CSV Format Requirements

### Input CSV (Your Local File)
Must contain columns:
- `originating_system_id`: The ID to match against the reference
- `mms_id`: The column to be updated (can be empty or contain existing values)

**Note:** Completely blank rows (all columns empty) are automatically removed during processing.

### Reference CSV (Network File)
Must contain columns:
- `Network Number`: The ID field that will be searched for substring matches
- `MMS Id`: The MMS ID value to copy to your CSV

## How Matching Works

The application uses **substring matching**:
- Your CSV's `originating_system_id` (e.g., `dg_1751378367`) is searched for within the reference CSV's `Network Number` field
- Example: `dg_1751378367` will match `http://hdl.handle.net/11084/1751378367; dg_1751378367`
- Requires exactly one match (ambiguous multiple matches are flagged as warnings)

## Output Files

The application creates a new file with the "UPDATED_" prefix:
- Original file: `Photos_For_DG.csv` (preserved unchanged)
- Updated file: `UPDATED_Photos_For_DG.csv` (created in same directory)

This ensures your original file is never modified.

## Logging

All operations are logged to timestamped files in the `logs/` directory:
- Format: `logs/alma_csv_updater_YYYYMMDD_HHMMSS.log`
- Includes: file selections, blank rows removed, matches found, warnings, errors
- Console output mirrors log file content

## Troubleshooting

### Network Connection Issues
- Ensure the network share is mounted at `/Volumes/MEDIADB/`
- Check file permissions for the reference CSV
- Verify the reference CSV path: `/Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`

### CSV Format Issues
- Ensure your CSV has the required columns: `originating_system_id` and `mms_id`
- Check that the reference CSV has "Network Number" and "MMS Id" columns
- Make sure files are UTF-8 encoded

### Not Found Entries
- Rows marked with "NOT FOUND IN ALMA" timestamps will be re-processed on subsequent runs
- Check logs for specific `originating_system_id` values that weren't found
- Verify IDs exist in the reference CSV

## Development

To contribute or modify:

1. Make your changes to `app.py`
2. Test thoroughly with sample CSV files
3. Check logs for any warnings or errors
4. Submit a pull request with a clear description of changes

## License

This project is provided as-is for use within the organization.
