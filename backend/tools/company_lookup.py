"""
Company Lookup — Maps product names to their parent companies.

When a competitor is a product (not a standalone company), agents should
search the PARENT company for accurate data — especially for hiring signals.

e.g. "Confluence hiring" → very few results
     "Atlassian hiring"  → thousands of results with real signals
"""

# Maps lowercase product/brand name → parent company name
PARENT_COMPANY_MAP = {
    # Atlassian
    "confluence":   "Atlassian",
    "jira":         "Atlassian",
    "trello":       "Atlassian",
    "bitbucket":    "Atlassian",
    "statuspage":   "Atlassian",
    # Salesforce
    "slack":        "Salesforce",
    "tableau":      "Salesforce",
    "heroku":       "Salesforce",
    # Microsoft
    "github":       "Microsoft",
    "linkedin":     "Microsoft",
    "teams":        "Microsoft",
    "azure":        "Microsoft",
    "xbox":         "Microsoft",
    # Google / Alphabet
    "youtube":      "Google",
    "gmail":        "Google",
    "google docs":  "Google",
    "google drive": "Google",
    "google workspace": "Google",
    "android":      "Google",
    "nest":         "Google",
    # Meta
    "instagram":    "Meta",
    "whatsapp":     "Meta",
    "messenger":    "Meta",
    "threads":      "Meta",
    # Adobe
    "photoshop":    "Adobe",
    "illustrator":  "Adobe",
    "premiere":     "Adobe",
    "acrobat":      "Adobe",
    "adobe xd":     "Adobe",
    # Apple
    "icloud":       "Apple",
    "facetime":     "Apple",
    "imessage":     "Apple",
    # Amazon
    "aws":          "Amazon",
    "alexa":        "Amazon",
    "kindle":       "Amazon",
    "twitch":       "Amazon",
    "goodreads":    "Amazon",
    # Bytedance
    "tiktok":       "ByteDance",
    # Intuit
    "quickbooks":   "Intuit",
    "mailchimp":    "Intuit",
    "turbotax":     "Intuit",
    # Hubspot products (HubSpot is standalone but has sub-products)
    # Zendesk
    "sunshine":     "Zendesk",
}


def get_parent_company(competitor: str) -> str | None:
    """
    Returns the parent company for a known product name, or None if the
    competitor IS its own company (e.g. Notion, Linear, Vercel).
    """
    return PARENT_COMPANY_MAP.get(competitor.lower().strip())


def get_display_name(competitor: str) -> str:
    """
    Returns a display name that shows parent context when relevant.
    e.g. "Confluence" → "Confluence (by Atlassian)"
         "Notion"     → "Notion"
    """
    parent = get_parent_company(competitor)
    if parent:
        return f"{competitor} (by {parent})"
    return competitor


def get_search_name(competitor: str, category: str) -> str:
    """
    Returns the best name to use in a search query for a given category.
    For hiring especially, the parent company yields far better results.
    """
    parent = get_parent_company(competitor)
    if parent and category == "hiring":
        # Search parent company for hiring — "Atlassian hiring" not "Confluence hiring"
        return parent
    if parent and category == "news":
        # Include both for news — captures product AND company news
        return f"{competitor} {parent}"
    return competitor
