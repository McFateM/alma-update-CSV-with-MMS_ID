#!/usr/bin/env python3
"""
Alma CSV Updater - A Flet application to update CSV files with MMS IDs
from a network reference CSV file.
"""

import flet as ft
import pandas as pd
import os
from pathlib import Path
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
import tempfile
import io


class AlmaCSVUpdater:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Alma CSV Updater"
        self.page.window_width = 800
        self.page.window_height = 600
        
        self.selected_csv_path = None
        self.reference_df = None
        self.progress_text = ft.Text("")
        self.status_text = ft.Text("", color=ft.colors.BLUE)
        
        # SMB connection details
        self.smb_server = "storage"
        self.smb_share = "MEDIADB"
        self.smb_path = "DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the Flet UI components"""
        
        # File picker for selecting local CSV
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        # Selected file display
        self.selected_file_text = ft.Text("No file selected", italic=True)
        
        # Buttons
        self.select_button = ft.ElevatedButton(
            "Select CSV File",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["csv"],
                dialog_title="Select CSV file to update"
            )
        )
        
        self.process_button = ft.ElevatedButton(
            "Process and Update",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.process_csv,
            disabled=True
        )
        
        # Progress indicator
        self.progress_bar = ft.ProgressBar(visible=False, width=400)
        
        # Main layout
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Alma CSV Updater", size=30, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Select a local CSV file to update with MMS IDs:", size=16),
                    ft.Row([self.select_button]),
                    self.selected_file_text,
                    ft.Divider(),
                    ft.Row([self.process_button]),
                    self.progress_bar,
                    self.progress_text,
                    self.status_text,
                ], spacing=20),
                padding=40
            )
        )
        
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection event"""
        if e.files and len(e.files) > 0:
            self.selected_csv_path = e.files[0].path
            self.selected_file_text.value = f"Selected: {os.path.basename(self.selected_csv_path)}"
            self.process_button.disabled = False
            self.status_text.value = ""
            self.status_text.color = ft.colors.BLUE
        else:
            self.selected_csv_path = None
            self.selected_file_text.value = "No file selected"
            self.process_button.disabled = True
            
        self.page.update()
        
    def load_reference_csv_from_smb(self):
        """Load the reference CSV file from SMB share"""
        try:
            self.update_progress("Connecting to network share...")
            
            # For SMB connection, we need credentials
            # Trying anonymous connection first
            conn = SMBConnection("", "", "client", self.smb_server, use_ntlm_v2=True)
            
            # Try to connect (this might fail without proper credentials)
            # Using port 445 for SMB
            if not conn.connect(self.smb_server, 445):
                raise Exception("Failed to connect to SMB server")
                
            self.update_progress("Connected. Downloading reference CSV...")
            
            # Download file to memory
            file_obj = io.BytesIO()
            conn.retrieveFile(self.smb_share, self.smb_path, file_obj)
            
            # Read CSV from memory
            file_obj.seek(0)
            # Read Network Number and MMS Id as strings to preserve format
            self.reference_df = pd.read_csv(file_obj, dtype={'Network Number': str, 'MMS Id': str})
            
            conn.close()
            
            self.update_progress(f"Reference CSV loaded: {len(self.reference_df)} records")
            return True
            
        except Exception as e:
            # If SMB fails, try to load from a local copy if available
            local_path = "/tmp/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv"
            if os.path.exists(local_path):
                self.update_progress(f"SMB access failed, using local copy: {str(e)}")
                # Read Network Number and MMS Id as strings to preserve format
                self.reference_df = pd.read_csv(local_path, dtype={'Network Number': str, 'MMS Id': str})
                return True
            else:
                self.update_status(f"Error loading reference CSV: {str(e)}", error=True)
                return False
    
    def update_progress(self, message):
        """Update progress text"""
        self.progress_text.value = message
        self.page.update()
        
    def update_status(self, message, error=False):
        """Update status text"""
        self.status_text.value = message
        self.status_text.color = ft.colors.RED if error else ft.colors.GREEN
        self.page.update()
        
    def process_csv(self, e):
        """Process the selected CSV file and update MMS IDs"""
        if not self.selected_csv_path:
            self.update_status("Please select a CSV file first", error=True)
            return
            
        try:
            # Show progress
            self.progress_bar.visible = True
            self.process_button.disabled = True
            self.select_button.disabled = True
            self.page.update()
            
            # Load reference CSV if not already loaded
            if self.reference_df is None:
                if not self.load_reference_csv_from_smb():
                    return
            
            # Load the selected CSV
            self.update_progress("Loading selected CSV file...")
            # Read mms_id and originating_system_id as strings to preserve format
            df = pd.read_csv(self.selected_csv_path, dtype={'mms_id': str, 'originating_system_id': str})
            
            # Check for required columns
            if 'originating_system_id' not in df.columns:
                self.update_status("Error: 'originating_system_id' column not found in CSV", error=True)
                return
                
            if 'mms_id' not in df.columns:
                # Add mms_id column if it doesn't exist
                df['mms_id'] = ''
            
            # Replace 'nan' strings with empty strings (from reading with dtype=str)
            df['originating_system_id'] = df['originating_system_id'].replace('nan', '')
            df['mms_id'] = df['mms_id'].replace('nan', '')
            
            # Check reference CSV columns
            if 'Network Number' not in self.reference_df.columns:
                self.update_status("Error: 'Network Number' column not found in reference CSV", error=True)
                return
                
            if 'MMS Id' not in self.reference_df.columns:
                self.update_status("Error: 'MMS Id' column not found in reference CSV", error=True)
                return
            
            # Create lookup dictionary from reference CSV
            mms_lookup = {}
            for _, row in self.reference_df.iterrows():
                network_num = row['Network Number']
                mms_id = row['MMS Id']
                # Check if values are not empty strings (after dtype=str conversion)
                if network_num and network_num != 'nan' and mms_id and mms_id != 'nan':
                    mms_lookup[str(network_num).strip()] = str(mms_id).strip()
            
            self.update_progress(f"Reference lookup created with {len(mms_lookup)} entries")
            
            # Process each row
            updated_count = 0
            skipped_count = 0
            not_found_count = 0
            
            total_rows = len(df)
            for idx, row in df.iterrows():
                # Update progress
                if idx % 10 == 0:
                    self.update_progress(f"Processing row {idx + 1} of {total_rows}...")
                
                # Check if mms_id is empty and originating_system_id is valid
                mms_id_val = str(row['mms_id']).strip()
                orig_id_val = str(row['originating_system_id']).strip()
                
                if not mms_id_val or mms_id_val == 'nan':
                    if orig_id_val and orig_id_val != 'nan':
                        # Look up MMS ID
                        if orig_id_val in mms_lookup:
                            df.at[idx, 'mms_id'] = mms_lookup[orig_id_val]
                            updated_count += 1
                        else:
                            not_found_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Already has mms_id
                    skipped_count += 1
            
            # Save updated CSV
            self.update_progress("Saving updated CSV...")
            df.to_csv(self.selected_csv_path, index=False)
            
            # Show results
            result_message = f"Processing complete!\n"
            result_message += f"Updated: {updated_count} rows\n"
            result_message += f"Skipped (already had mms_id or no originating_system_id): {skipped_count} rows\n"
            result_message += f"Not found in reference: {not_found_count} rows"
            
            self.update_status(result_message, error=False)
            self.update_progress(f"File saved: {os.path.basename(self.selected_csv_path)}")
            
        except Exception as ex:
            self.update_status(f"Error processing CSV: {str(ex)}", error=True)
            import traceback
            print(traceback.format_exc())
            
        finally:
            # Hide progress and re-enable buttons
            self.progress_bar.visible = False
            self.process_button.disabled = False
            self.select_button.disabled = False
            self.page.update()


def main(page: ft.Page):
    """Main entry point for the Flet application"""
    AlmaCSVUpdater(page)


if __name__ == "__main__":
    ft.app(target=main)
