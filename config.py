"""Configuration and constants for the prospecting trigger agent."""

# High-impact trigger types to look for
TRIGGER_TYPES = [
    "M&A Activity",
    "Funding Round (Series B+)",
    "IPO Preparation",
    "IPO Completed",
    "Private Equity Acquisition",
    "Executive Change (CIO/CFO/CHRO/COO/VP)",
    "Geographic Expansion",
    "New Office Opening",
    "Headcount Growth (100+ hires)",
    "Digital Transformation Initiative",
    "Legacy System Migration (SAP/Oracle/PeopleSoft)",
    "Cloud Migration Project",
    "System Outage or IT Failure",
    "Restructuring or Reorganization",
    "Compliance Issue",
    "New Regulatory Requirement",
    "Remote/Hybrid Work Policy Change",
    "Operational Challenges (Earnings)",
    "Industry Award (Inc 5000/Fast Company/Best Places to Work)",
]

# NewsAPI settings
NEWS_LOOKBACK_DAYS = 30  # Free tier only allows ~30 days back
MAX_ARTICLES_PER_COMPANY = 10

# Claude settings
CLAUDE_MODEL = "claude-3-5-haiku-latest"
