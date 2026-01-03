"""Google Sheets client for reading companies and writing triggers."""

import os
from dataclasses import dataclass

import gspread
from google.oauth2.service_account import Credentials


@dataclass
class Company:
    """Represents a company row from the sheet."""
    name: str
    website: str
    row_number: int
    latest_trigger: str = ""
    trigger_date: str = ""
    article_link: str = ""
    trigger_type: str = ""


class SheetsClient:
    """Client for reading/writing to Google Sheets."""

    # Expected column headers
    COLUMNS = [
        "Company Name",
        "Website",
        "Latest Trigger",
        "Trigger Date",
        "Article Link",
        "Trigger Type",
    ]

    def __init__(self, sheet_id: str, credentials_path: str = "credentials.json"):
        """Initialize the Sheets client.

        Args:
            sheet_id: The Google Sheet ID (from URL)
            credentials_path: Path to service account JSON file
        """
        self.sheet_id = sheet_id
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def read_companies(self) -> list[Company]:
        """Read all companies from the sheet.

        Returns:
            List of Company objects with their data and row numbers
        """
        all_values = self.sheet.get_all_values()

        if not all_values:
            return []

        # First row is headers
        headers = all_values[0]
        companies = []

        for row_idx, row in enumerate(all_values[1:], start=2):  # Row 2 onwards
            if not row or not row[0].strip():  # Skip empty rows
                continue

            # Pad row to have all columns
            while len(row) < len(self.COLUMNS):
                row.append("")

            companies.append(Company(
                name=row[0].strip(),
                website=row[1].strip() if len(row) > 1 else "",
                row_number=row_idx,
                latest_trigger=row[2].strip() if len(row) > 2 else "",
                trigger_date=row[3].strip() if len(row) > 3 else "",
                article_link=row[4].strip() if len(row) > 4 else "",
                trigger_type=row[5].strip() if len(row) > 5 else "",
            ))

        return companies

    def update_trigger(
        self,
        row_number: int,
        trigger_summary: str,
        trigger_type: str,
        trigger_date: str,
        article_link: str,
    ) -> None:
        """Update a company row with trigger information.

        Args:
            row_number: The 1-indexed row number to update
            trigger_summary: Summary of the trigger event
            trigger_type: Category of trigger (e.g., "M&A Activity")
            trigger_date: Date of the trigger article
            article_link: URL to the source article
        """
        # Update columns C through F (indices 3-6 in 1-indexed)
        self.sheet.update(
            f"C{row_number}:F{row_number}",
            [[trigger_summary, trigger_date, article_link, trigger_type]],
        )
