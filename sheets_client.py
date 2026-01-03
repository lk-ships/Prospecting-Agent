"""Google Sheets client for reading companies and writing triggers."""

import os
from dataclasses import dataclass
from typing import List, Set, Tuple

import gspread
from google.oauth2.service_account import Credentials


@dataclass
class Company:
    """Represents a company from the sheet."""
    name: str
    website: str


class SheetsClient:
    """Client for reading/writing to Google Sheets."""

    # Expected column headers
    COLUMNS = [
        "Company Name",
        "Website",
        "Trigger Summary",
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

    def read_companies(self) -> List[Company]:
        """Read unique companies from the sheet.

        Returns:
            List of unique Company objects (by name)
        """
        all_values = self.sheet.get_all_values()

        if not all_values:
            return []

        # Track unique companies by name
        seen_names = set()  # type: Set[str]
        companies = []

        for row_idx, row in enumerate(all_values[1:], start=2):  # Row 2 onwards
            if not row or not row[0].strip():  # Skip empty rows
                continue

            name = row[0].strip()

            # Skip if we've already seen this company
            if name.lower() in seen_names:
                continue

            seen_names.add(name.lower())
            companies.append(Company(
                name=name,
                website=row[1].strip() if len(row) > 1 else "",
            ))

        return companies

    def get_existing_triggers(self) -> Set[Tuple[str, str]]:
        """Get set of (company_name, article_link) pairs already in sheet.

        Used to avoid adding duplicate triggers.
        """
        all_values = self.sheet.get_all_values()
        existing = set()  # type: Set[Tuple[str, str]]

        for row in all_values[1:]:  # Skip header
            if len(row) >= 5 and row[0].strip() and row[4].strip():
                existing.add((row[0].strip().lower(), row[4].strip()))

        return existing

    def append_trigger(
        self,
        company_name: str,
        website: str,
        trigger_summary: str,
        trigger_type: str,
        trigger_date: str,
        article_link: str,
    ) -> None:
        """Append a new row with trigger information.

        Args:
            company_name: Name of the company
            website: Company website
            trigger_summary: Summary of the trigger event
            trigger_type: Category of trigger (e.g., "M&A Activity")
            trigger_date: Date of the trigger article
            article_link: URL to the source article
        """
        self.sheet.append_row(
            [company_name, website, trigger_summary, trigger_date, article_link, trigger_type],
            value_input_option="USER_ENTERED",
        )
