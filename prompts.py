'''
prompts.py code file.
'''

def system_prompt():
    '''
    Returns the system prompt for the data cleaning assistant.
    Instruct the assistant to extract only valid individual contact information and ignore any irrelevant data.
    '''
    return (
        "You are an expert data cleaning assistant. Your task is to extract and clean only valid individual contact "
        "information from an Excel file that contains a mix of relevant contact data and irrelevant data (such as flight "
        "details, hotel names, addresses, and group booking information). Process only rows that represent a single "
        "individual's contact with a name and a phone number. Apply strict cleaning rules and ignore any non-contact data."
    )

def bulk_content_prompt(contacts_data):
    '''
    Returns the content prompt for cleaning multiple contacts in bulk.

    Args:
        contacts_data (str): A string containing multiple contacts in the format "Name: <name>, Phone: <phone>"
                           with each contact on a new line.

    Returns:
        str: The formatted prompt for bulk processing.
    '''
    template = """
You are provided with a list of raw contact data extracted from an Excel file.
Your task is to clean and validate each contact in the list.

Apply the following rules to EACH contact:
1. Process only entries that represent individual contact information.
2. Skip any entries containing:
   - Hotel names
   - Flight information
   - Addresses
   - Group booking details
   - Tour guide/leader information
   - Any other non-individual contact data
3. For each valid contact:
   - Remove titles (Mr., Ms., Mrs., Dr., etc.)
   - Remove extra spaces
   - Standardize phone numbers to +90XXXXXXXXXX format
   - For phone numbers:
     * If starts with '+90': keep as is
     * If starts with '90', '0', '090', or '0090': remove and add '+90'
     * If no prefix: add '+90'

Return a JSON array where each element has 'name' and 'phone' keys.
Skip invalid contacts entirely (do not include them in the output array).

Examples of Processing:

Input Contacts:
Name: Mr. John Smith, Phone: 05321234567
Name: Hotel Booking, Phone: ABC123
Name: Ms. Jane Doe, Phone: 90505987654
Name: Tour Guide Info, Phone: 123456

Expected Output:
[
    {{"name": "John Smith", "phone": "+905321234567"}},
    {{"name": "Jane Doe", "phone": "+90505987654"}}
]

Notice that the hotel booking and tour guide entries are completely omitted.

Now, process these contacts:
{contacts_data}
"""
    return template.format(contacts_data=contacts_data)