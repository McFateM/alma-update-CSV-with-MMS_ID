# Workflow - Alma Update CSV with MMS IDs

This is the suggested workflow for using this app.  

1) Begin by mapping the network //Storage/MEDIADB/DGIngest drive to your workstation.  That directory should contain a CSV file named `All-Digital-Items-MMS_ID-with-File-Internal-Path.csv`.  If it does not, or if an update is needed, you will need to generate that file and save it to the `//Storage/MEDIADB/DGIngest` directory using Steps 1a through 1d.  If an up-to-date copy of the file already exists, skip ahead to Step 2.

1a) Open _Alma_, navigate to `Analytics` and `Access Analytics`, and from the upper-right corner select `Open` and choose `All-Digital-Items-MMS_ID-with-File-Internal-Path`.

1b) Then choose `Export this analysis`, `Data`, and `CSV`.  This should produce an up-to-date export of all digital titles including a `Network Number` and `MMS Id` fields in a file named `All-Digital-Items-MMS_ID-with-File-Internal-Path.csv` on your workstation.  

1c) Copy the new exported .csv file to `//Storage/MEDIADB/DGIngest` replacing any copy that might already exist there.

2) The CSV file that you wish to update should be found in the suppressed `Import CSV Artifacts` collection within `DigitalGrinnell`.  Navigate to the appropriate representation and download the .csv file from _Alma_ to your workstation.  Warning: This may take lots of clicks!  It's _Alma_, what more do I need to say?

3) Run the `alma-update-CSV-with-MMS_ID` app by navigating to its directory on your workstation, and using `./run.sh` (for Mac) or `./run.bat` (for Windows).

4) In the app, select the CSV file you downloaded from `Import CSV Artifacts` and click the `Process and Update` button.  

5) Sit back and watch, but the app should finish in a matter of seconds, not minutes.  When complete, the selected CSV file should be updated with a new name that has `UPDATED_` prepended to the original file name.

6) Take note of any errors or warnings, but if all goes well the `UPDATED_` copy of the CSV file you selected should be updated with `MMS IDs` for any digital titles found in _Alma_.  

7) Consider updating the `Import CSV Artifacts` representation of the CSV file using the file that the app just updated.

8) Repeat Steps 2-7 for each CSV file you wish to update in `Import CSV Artifacts`.  