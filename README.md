# alma-update-CSV-with-MMS_ID

A Flet/Python desktop application to update the `mms_id` column of a selected CSV file using information gathered from the network reference CSV file at `smb://storage/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`.

## Features

- **Simple GUI**: Single-page Flet interface for easy file selection and processing
- **CSV Processing**: Opens and processes local CSV files
- **Network Integration**: Accesses reference data from SMB network share
- **Automatic Matching**: Matches `originating_system_id` with "Network Number" from reference CSV
- **Smart Updates**: Only updates rows with empty `mms_id` and valid `originating_system_id`
- **Progress Tracking**: Visual feedback during processing
- **Error Handling**: Comprehensive error handling and user feedback

## Requirements

- Python 3.8 or higher
- Access to the network share `smb://storage/MEDIADB/`

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

1. Run the application:
   ```bash
   python app.py
   ```

2. Click "Select CSV File" to choose your local CSV file that needs updating

3. Click "Process and Update" to start the update process

4. The application will:
   - Connect to the network share
   - Load the reference CSV
   - Match `originating_system_id` values with "Network Number" from the reference
   - Update empty `mms_id` cells with corresponding "MMS Id" values
   - Save the updated CSV back to the original file

## CSV Format Requirements

### Input CSV (Your Local File)
Must contain columns:
- `originating_system_id`: The ID to match against the reference
- `mms_id`: The column to be updated (can be empty or contain existing values)

### Reference CSV (Network File)
Must contain columns:
- `Network Number`: The ID to match against
- `MMS Id`: The MMS ID value to copy to your CSV

## Fallback Mode

If the SMB network share is not accessible, you can place a local copy of the reference CSV at:
```
/tmp/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv
```

The application will automatically use this local copy if network access fails.

## Troubleshooting

### Network Connection Issues
- Ensure you have network access to `smb://storage/MEDIADB/`
- Check your network credentials and permissions
- Try using the local fallback file if network access is unavailable

### CSV Format Issues
- Ensure your CSV has the required columns: `originating_system_id` and `mms_id`
- Check that the reference CSV has "Network Number" and "MMS Id" columns
- Make sure files are UTF-8 encoded

## Development

To contribute or modify:

1. Make your changes to `app.py`
2. Test thoroughly with sample CSV files
3. Submit a pull request with a clear description of changes

## License

This project is provided as-is for use within the organization.
