'''
prompts.py code file.
'''

def system_prompt():
    '''
    Returns the system prompt for the data cleaning assistant.
    Includes comprehensive rules for filtering travel industry specific data.
    '''
    return (
        "You are an expert data cleaning assistant specialized in extracting individual traveler "
        "contact information from complex travel industry spreadsheets. Your task is to identify "
        "and clean only valid individual contact information while strictly filtering out all "
        "travel-related metadata, locations, and operational information.\n\n"
        "A valid contact MUST:\n"
        "1. Be a single individual's name (first and last name)\n"
        "2. Have no location codes, titles, or role indicators\n"
        "3. Not be part of operational or logistical information\n\n"
        "You MUST exclude ANY entry that contains:\n"
        "- Tour leader/guide information (e.g., 'Tour Leaders', 'Guide')\n"
        "- Location codes in parentheses (e.g., '(SFO)', '(NYC)', '(MIA)', '(LAX)', '(LAS)', '(ORL)')\n"
        "- Company or organization names (e.g., 'KANTARA', 'BUSA', 'SLL')\n"
        "- Hotel names and addresses\n"
        "- Meeting room or storage information\n"
        "- City names or location information\n"
        "- Multiple names connected by '&' or 'and'\n"
        "- Travel dates or schedule information"
    )

def bulk_content_prompt(contacts_data):
    '''
    Returns the content prompt for cleaning multiple contacts in bulk.
    Includes detailed examples from travel industry data.
    '''
    template = """
You are processing raw contact data from a travel industry spreadsheet. Your task is to identify and clean ONLY valid individual traveler contact information.

STRICT FILTERING RULES - Exclude ANY entry containing:

1. Tour Leader/Guide Information:
   - "Tour Leaders Sedef O'BRIEN (SFO)"
   - "Tour Leader Kivanc ONER (MIA&ORL)"
   - Any entry with tour guide indicators

2. Location Codes:
   - (SFO), (NYC), (MIA), (LAX), (LAS), (ORL)
   - Any parenthetical location abbreviations

3. City Names and Addresses:
   - "San Francisco"
   - "Miami"
   - "Las Vegas"
   - "New York"
   - "Los Angeles"
   - "Orlando"
   - Any street addresses or zip codes

4. Hotel and Venue Information:
   - "Hilton Garden Inn"
   - "Treasure Island"
   - "Sheraton"
   - "Doubletree"
   - Any hotel or venue names

5. Operational Information:
   - "Meeting room for storage"
   - "Meeting space TBA"
   - Room numbers or types
   - Dates or schedules

6. Company/Organization Names:
   - "KANTARA"
   - "BUSA"
   - "SLL"
   - Any business names

7. Multiple Names or Combined Entries:
   - "Sedef O'BRIEN & Pelin AKMAN"
   - Any entries with '&' or 'and'

For VALID contacts, clean as follows:
1. Remove all titles (Mr., Ms., Mrs., Dr., etc.)
2. Remove extra spaces
3. Format phone numbers:
   - Add '+90' prefix if missing
   - Remove '90', '0', '090', or '0090' prefix
   - Keep existing '+90' prefix

Examples:

VALID (Include):
Input: "Mr. OZGUR AKSOY, 05321234567"
Output: {{"name": "OZGUR AKSOY", "phone": "+905321234567"}}

INVALID (Exclude):
"Tour Leaders Sedef O'BRIEN (SFO)" -> SKIP
"Miami Hilton Garden Inn" -> SKIP
"Meeting room for storage Park 5" -> SKIP
"Sedef O'BRIEN & Pelin AKMAN (LAS&LAX)" -> SKIP

"Output ONLY valid JSON with no additional text."

Now, process these contacts:
{contacts_data}
"""
    return template.format(contacts_data=contacts_data)