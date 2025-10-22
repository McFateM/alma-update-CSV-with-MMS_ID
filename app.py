#!/usr/bin/env python3
"""
Alma CSV Updater - A Flet application to update CSV files with MMS IDs
from a network reference CSV file.
"""

import flet as ft
import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime


class AlmaCSVUpdater:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Alma CSV Updater"
        self.page.window_width = 800
        self.page.window_height = 600
        
        self.selected_csv_path = None
        self.reference_df = None
        self.progress_text = ft.Text("")
        self.status_text = ft.Text("", color=ft.Colors.BLUE)
        self.warning_text = ft.Text("", color=ft.Colors.RED)
        self.reference_path_text = ft.Text("", size=11, italic=True, color=ft.Colors.GREY_700)
        
        # Workflow dialog
        self.workflow_dialog = None
        
        # Local network path
        self.reference_csv_path = "/Volumes/MEDIADB/DGIngest/All-Digital-Items-MMS_ID-with-File-Internal-Path.csv"
        
        # Setup logging
        self.setup_logging()
        
        self.setup_ui()
        
        # Display reference CSV path in UI
        self.reference_path_text.value = f"Reference CSV: {self.reference_csv_path}"
    
    def setup_logging(self):
        """Setup logging to file and console"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"alma_csv_updater_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("Alma CSV Updater started")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 60)
        
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
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["csv"],
                dialog_title="Select CSV file to update"
            )
        )
        
        self.process_button = ft.ElevatedButton(
            "Process and Update",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.process_csv,
            disabled=True
        )
        
        self.workflow_button = ft.ElevatedButton(
            "Display WORKFLOW Instructions",
            icon=ft.Icons.HELP_OUTLINE,
            on_click=self.show_workflow
        )
        
        # Progress indicator
        self.progress_bar = ft.ProgressBar(visible=False, width=400)
        
        # Main layout with scrolling
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Alma CSV Updater", size=30, weight=ft.FontWeight.BOLD),
                    self.reference_path_text,
                    ft.Row([self.workflow_button]),
                    ft.Divider(),
                    ft.Text("Select a local CSV file to update with MMS IDs:", size=16),
                    ft.Row([self.select_button]),
                    self.selected_file_text,
                    ft.Divider(),
                    ft.Row([self.process_button]),
                    self.progress_bar,
                    self.progress_text,
                    self.status_text,
                    self.warning_text,
                ], spacing=20, scroll=ft.ScrollMode.AUTO),
                padding=40,
                expand=True
            )
        )
        
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection event"""
        if e.files and len(e.files) > 0:
            self.selected_csv_path = e.files[0].path
            self.selected_file_text.value = f"Selected CSV: {self.selected_csv_path}"
            self.process_button.disabled = False
            self.status_text.value = ""
            self.status_text.color = ft.Colors.BLUE
            self.logger.info(f"File selected: {self.selected_csv_path}")
        else:
            self.selected_csv_path = None
            self.selected_file_text.value = "No file selected"
            self.process_button.disabled = True
            self.logger.info("File selection cancelled")
            
        self.page.update()
        
    def show_workflow(self, e):
        """Display the WORKFLOW.md content in a dialog"""
        try:
            # Read WORKFLOW.md file
            workflow_path = Path(__file__).parent / "WORKFLOW.md"
            if not workflow_path.exists():
                workflow_content = "WORKFLOW.md file not found."
                self.logger.warning(f"WORKFLOW.md not found at {workflow_path}")
            else:
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    workflow_content = f.read()
                self.logger.info("Displayed WORKFLOW instructions")
            
            # Create dialog with scrollable content
            def close_dialog(e):
                self.workflow_dialog.open = False
                self.page.update()
            
            self.workflow_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Workflow Instructions", size=24, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([
                        ft.Markdown(
                            workflow_content,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            md_style_sheet=ft.MarkdownStyleSheet(
                                blockquote_text_style=ft.TextStyle(bgcolor=ft.Colors.GREY_200, color=ft.Colors.BLACK87, size=14, weight=ft.FontWeight.BOLD),
                                p_text_style=ft.TextStyle(color=ft.Colors.BLACK87, size=14, weight=ft.FontWeight.NORMAL),
                                code_text_style=ft.TextStyle(color=ft.Colors.RED_800, size=14, weight=ft.FontWeight.BOLD),
                            ),
                        ),
                    ], scroll=ft.ScrollMode.AUTO),
                    width=700,
                    height=500,
                ),
                actions=[
                    ft.TextButton("Close", on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.overlay.append(self.workflow_dialog)
            self.workflow_dialog.open = True
            self.page.update()
            
        except Exception as ex:
            self.logger.error(f"Error displaying workflow: {str(ex)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.update_status(f"Error displaying workflow: {str(ex)}", error=True)
    
    def load_reference_csv_from_smb(self):
        """Load the reference CSV file from local network path"""
        try:
            self.update_progress("Loading reference CSV from network share...")
            self.logger.info(f"Loading reference CSV from: {self.reference_csv_path}")
            
            # Check if the path exists
            if not os.path.exists(self.reference_csv_path):
                error_msg = f"Reference CSV not found at: {self.reference_csv_path}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # Read Network Number and MMS Id as strings to preserve format
            self.reference_df = pd.read_csv(self.reference_csv_path, dtype={'Network Number': str, 'MMS Id': str})
            
            # Log column names for debugging
            self.logger.info(f"Reference CSV columns: {list(self.reference_df.columns)}")
            
            self.update_progress(f"Reference CSV loaded: {len(self.reference_df)} records")
            self.logger.info(f"Reference CSV loaded successfully: {len(self.reference_df)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading reference CSV: {str(e)}")
            self.update_status(f"Error loading reference CSV: {str(e)}", error=True)
            return False
    
    def update_progress(self, message):
        """Update progress text"""
        self.progress_text.value = message
        self.page.update()
        
    def update_status(self, message, error=False):
        """Update status text"""
        self.status_text.value = message
        self.status_text.color = ft.Colors.RED if error else ft.Colors.GREEN
        self.page.update()
        
    def process_csv(self, e):
        """Process the selected CSV file and update MMS IDs"""
        if not self.selected_csv_path:
            self.update_status("Please select a CSV file first", error=True)
            self.logger.warning("Process attempted without file selection")
            return
            
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting CSV processing")
            self.logger.info(f"Selected file: {self.selected_csv_path}")
            
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
            self.logger.info("Loading selected CSV file...")
            # Read mms_id and originating_system_id as strings to preserve format
            df = pd.read_csv(self.selected_csv_path, dtype={'mms_id': str, 'originating_system_id': str})
            original_row_count = len(df)
            self.logger.info(f"Selected CSV loaded: {original_row_count} rows")
            
            # Remove completely blank rows
            df = df.dropna(how='all')
            blank_rows_removed = original_row_count - len(df)
            if blank_rows_removed > 0:
                self.logger.info(f"Removed {blank_rows_removed} blank rows from CSV")
            
            self.logger.info(f"Processing {len(df)} non-blank rows")
            
            # Check for required columns
            if 'originating_system_id' not in df.columns:
                error_msg = "Error: 'originating_system_id' column not found in CSV"
                self.logger.error(error_msg)
                self.update_status(error_msg, error=True)
                return
                
            if 'mms_id' not in df.columns:
                # Add mms_id column if it doesn't exist
                self.logger.info("Adding 'mms_id' column to CSV")
                df['mms_id'] = ''
            
            # Replace 'nan' strings with empty strings (from reading with dtype=str)
            df['originating_system_id'] = df['originating_system_id'].replace('nan', '')
            df['mms_id'] = df['mms_id'].replace('nan', '')
            
            # Check reference CSV columns
            if 'Network Number' not in self.reference_df.columns:
                error_msg = "Error: 'Network Number' column not found in reference CSV"
                self.logger.error(error_msg)
                self.update_status(error_msg, error=True)
                return
                
            if 'MMS Id' not in self.reference_df.columns:
                error_msg = "Error: 'MMS Id' column not found in reference CSV"
                self.logger.error(error_msg)
                self.update_status(error_msg, error=True)
                return
            
            # Create reference data structure for substring matching
            self.logger.info("Creating MMS ID lookup from reference CSV...")
            # Store as list of tuples (network_number, mms_id) for substring matching
            reference_data = []
            for _, row in self.reference_df.iterrows():
                network_num = row['Network Number']
                mms_id = row['MMS Id']
                # Check if values are not empty strings (after dtype=str conversion)
                if network_num and network_num != 'nan' and mms_id and mms_id != 'nan':
                    reference_data.append((str(network_num).strip(), str(mms_id).strip()))
            
            self.update_progress(f"Reference data loaded with {len(reference_data)} entries")
            self.logger.info(f"Reference data loaded with {len(reference_data)} entries")
            
            # Log sample entries from reference for debugging
            sample_entries = reference_data[:3]
            self.logger.info(f"Sample reference entries (Network Number, MMS Id): {sample_entries}")
            
            # Test search for the first originating_system_id to verify matching logic
            test_id = str(df['originating_system_id'].iloc[0]).strip()
            test_matches = [net_num for net_num, _ in reference_data if test_id in net_num]
            self.logger.info(f"Test search for first ID '{test_id}': found {len(test_matches)} matches")
            if test_matches:
                self.logger.info(f"Test match example: '{test_matches[0]}'")
            
            # Process each row
            self.logger.info(f"Processing {len(df)} rows...")
            updated_count = 0
            skipped_count = 0
            not_found_count = 0
            multiple_matches_count = 0
            not_found_samples = []  # Collect samples of not found IDs
            multiple_match_samples = []  # Collect samples of multiple matches
            
            total_rows = len(df)
            for idx, row in df.iterrows():
                # Update progress
                if idx % 10 == 0:
                    self.update_progress(f"Processing row {idx + 1} of {total_rows}...")
                
                # Check if mms_id is empty and originating_system_id is valid
                mms_id_val = str(row['mms_id']).strip()
                orig_id_val = str(row['originating_system_id']).strip()
                
                # Treat "NOT FOUND IN ALMA" entries as empty
                is_empty_mms_id = (not mms_id_val or 
                                   mms_id_val == 'nan' or 
                                   mms_id_val.startswith('NOT FOUND IN ALMA'))
                
                if is_empty_mms_id:
                    if orig_id_val and orig_id_val != 'nan':
                        # Find Network Numbers that contain the originating_system_id
                        all_matches = [(net_num, mms_id) for net_num, mms_id in reference_data 
                                       if orig_id_val in net_num]
                        
                        # Deduplicate matches by Network Number to avoid counting duplicates in reference data
                        # as multiple matches (only different Network Numbers should be considered multiple)
                        unique_matches = {}
                        for net_num, mms_id in all_matches:
                            if net_num not in unique_matches:
                                unique_matches[net_num] = mms_id
                        
                        matches = list(unique_matches.items())
                        
                        if len(matches) == 1:
                            # Exactly one match found
                            df.at[idx, 'mms_id'] = matches[0][1]
                            updated_count += 1
                        elif len(matches) > 1:
                            # Multiple matches found - ambiguous
                            multiple_matches_count += 1
                            if len(multiple_match_samples) < 3:
                                match_details = f"'{orig_id_val}' found in: {[m[0] for m in matches]}"
                                multiple_match_samples.append(match_details)
                            self.logger.warning(f"Row {idx + 1}: Multiple matches for '{orig_id_val}': {[m[0] for m in matches]}")
                        else:
                            # No matches found - mark with timestamp
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            not_found_marker = f"NOT FOUND IN ALMA - {timestamp}"
                            df.at[idx, 'mms_id'] = not_found_marker
                            not_found_count += 1
                            if len(not_found_samples) < 5:
                                not_found_samples.append(orig_id_val)
                            self.logger.warning(f"Row {idx + 1}: No match found for originating_system_id '{orig_id_val}'")
                    else:
                        skipped_count += 1
                else:
                    # Already has mms_id
                    skipped_count += 1
            
            # Log samples of issues for debugging
            if not_found_samples:
                self.logger.warning(f"Sample originating_system_id values not found in any Network Number: {not_found_samples}")
            if multiple_match_samples:
                self.logger.warning(f"Sample multiple match cases: {multiple_match_samples}")
            
            # Save updated CSV
            self.update_progress("Saving updated CSV...")
            self.logger.info("Saving updated CSV...")
            
            # Remove any trailing blank rows before saving
            df = df.dropna(how='all')
            
            # Create new filename with UPDATED_ prefix
            original_path = Path(self.selected_csv_path)
            new_filename = f"UPDATED_{original_path.name}"
            new_path = original_path.parent / new_filename
            
            df.to_csv(new_path, index=False)
            
            self.logger.info(f"CSV saved as: {new_path}")
            
            # Show results - main status in green
            result_message = f"Processing complete!\n"
            if blank_rows_removed > 0:
                result_message += f"Removed: {blank_rows_removed} blank rows\n"
            result_message += f"Updated: {updated_count} rows\n"
            result_message += f"Skipped (already had mms_id or no originating_system_id): {skipped_count} rows\n"
            result_message += f"Not found in reference: {not_found_count} rows\n"
            result_message += f"Multiple matches (ambiguous): {multiple_matches_count} rows"
            
            # Build warning message in red for not found items
            warning_message = ""
            if not_found_count > 0:
                warning_message += f"⚠️  WARNING: {not_found_count} rows not found in reference:\n"
                for sample in not_found_samples:
                    warning_message += f"  - {sample}\n"
                if not_found_count > len(not_found_samples):
                    warning_message += f"  ... and {not_found_count - len(not_found_samples)} more\n"
            
            if multiple_matches_count > 0:
                if warning_message:
                    warning_message += "\n"
                warning_message += f"⚠️  WARNING: {multiple_matches_count} rows with multiple matches:\n"
                for sample in multiple_match_samples:
                    warning_message += f"  - {sample}\n"
                if multiple_matches_count > len(multiple_match_samples):
                    warning_message += f"  ... and {multiple_matches_count - len(multiple_match_samples)} more\n"
            
            self.logger.info("=" * 60)
            self.logger.info("Processing complete!")
            if blank_rows_removed > 0:
                self.logger.info(f"Removed: {blank_rows_removed} blank rows")
            self.logger.info(f"Updated: {updated_count} rows")
            self.logger.info(f"Skipped (already had mms_id or no originating_system_id): {skipped_count} rows")
            
            if not_found_count > 0:
                self.logger.warning(f"Not found in reference: {not_found_count} rows")
            else:
                self.logger.info(f"Not found in reference: {not_found_count} rows")
            
            if multiple_matches_count > 0:
                self.logger.warning(f"Multiple matches (ambiguous): {multiple_matches_count} rows")
            else:
                self.logger.info(f"Multiple matches (ambiguous): {multiple_matches_count} rows")
                
            self.logger.info(f"File saved as: {new_path}")
            self.logger.info("=" * 60)
            
            # Show status in green, warnings in red
            self.update_status(result_message, error=False)
            self.warning_text.value = warning_message
            self.update_progress(f"Updated CSV saved to: {new_path}")
            
        except Exception as ex:
            self.logger.error(f"Error processing CSV: {str(ex)}")
            self.logger.exception("Full traceback:")
            self.update_status(f"Error processing CSV: {str(ex)}", error=True)
            
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
