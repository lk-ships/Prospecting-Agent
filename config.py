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

# Priority scoring based on buying intent
TRIGGER_PRIORITY = {
    # HIGH - Strong buying signals, urgent needs
    "M&A Activity": "High",
    "Private Equity Acquisition": "High",
    "Executive Change (CIO/CFO/CHRO/COO/VP)": "High",
    "Restructuring or Reorganization": "High",
    "Legacy System Migration (SAP/Oracle/PeopleSoft)": "High",
    "System Outage or IT Failure": "High",
    "IPO Preparation": "High",
    "IPO Completed": "High",
    "Compliance Issue": "High",
    "Operational Challenges (Earnings)": "High",

    # MEDIUM - Growth signals, planned initiatives
    "Funding Round (Series B+)": "Medium",
    "Geographic Expansion": "Medium",
    "New Office Opening": "Medium",
    "Headcount Growth (100+ hires)": "Medium",
    "Digital Transformation Initiative": "Medium",
    "Cloud Migration Project": "Medium",
    "New Regulatory Requirement": "Medium",
    "Remote/Hybrid Work Policy Change": "Medium",

    # LOW - Awareness, less urgent
    "Industry Award (Inc 5000/Fast Company/Best Places to Work)": "Low",
}

# NewsAPI settings
NEWS_LOOKBACK_DAYS = 30  # Free tier only allows ~30 days back
MAX_ARTICLES_PER_COMPANY = 10

# Claude settings
CLAUDE_MODEL = "claude-3-5-haiku-latest"
