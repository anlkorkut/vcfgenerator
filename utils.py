'''
utils.py code file.
'''

import pandas as pd
import json
import re
from collections import Counter
from prompts import system_prompt, bulk_content_prompt
from logger import init
from model_wrapper import ModelWrapper
import logging

# Define a duplicate filter to avoid duplicate log messages
class DuplicateFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.logged_messages = set()
    def filter(self, record):
        msg = record.getMessage()
        if msg in self.logged_messages:
            return False
        self.logged_messages.add(msg)
        return True

# Initialize logger and ensure single handler
# Logger setup
logger = init(__name__)
# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Create file handler
file_handler = logging.FileHandler('utils.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add DuplicateFilter to file handler
duplicate_filter = DuplicateFilter()
file_handler.addFilter(duplicate_filter)

# Add the file handler to logger
logger.addHandler(file_handler)

model_wrapper = ModelWrapper()

def standardize_phone(phone):
    '''
    Standardize a phone number according to Turkish format rules.
    - Remove any spaces, parentheses, or dashes.
    - If it starts with "0090", "090", "90", or "0", remove that prefix and prepend "+90".
    - If it already starts with "+90", do nothing.
    - Finally, take the last 10 digits and return the result in the format: +90XXXXXXXXXX.
    '''
    phone = str(phone).strip()
    if phone.endswith('.0'):
        phone = phone[:-2]
    phone = re.sub(r'[\s()-]', '', phone)

    if phone.startswith('+90'):
        standardized = phone
    elif phone.startswith('0090'):
        standardized = '+90' + phone[4:]
    elif phone.startswith('090'):
        standardized = '+90' + phone[3:]
    elif phone.startswith('90'):
        standardized = '+90' + phone[2:]
    elif phone.startswith('0'):
        standardized = '+90' + phone[1:]
    else:
        standardized = '+90' + phone

    if standardized.startswith('+90'):
        digits = standardized[3:]
        digits = digits[-10:]
        standardized = '+90' + digits
    return standardized

def is_turkish_mobile(phone):
    '''
    Check if a standardized phone number is a Turkish mobile number.
    Turkish mobile numbers must be in the format +90XXXXXXXXXX where the first digit of the local part is 5.
    '''
    return phone.startswith('+90') and len(phone) == 13 and phone[3] == '5'

def preprocess_excel(file):
    '''
    Preprocess the Excel file to extract and clean relevant columns.
    Returns a DataFrame with columns "Names", "Phone", and "Room" (if available).
    '''
    logger.info("=== Starting Excel Preprocessing ===")
    try:
        # Read raw Excel data
        df = pd.read_excel(file, header=2)
        logger.info(f"Raw Excel data loaded: {len(df)} rows")
        logger.info("Initial columns found: " + ", ".join([str(col) for col in df.columns.tolist()]))

        # Log sample of raw data safely
        logger.info("Sample of raw data (first 5 rows):")
        for idx, row in df.head().iterrows():
            try:
                names = str(row['Names']) if pd.notna(row['Names']) else 'NULL'
                phone = str(row['Phone']) if pd.notna(row['Phone']) else 'NULL'
                logger.info(f"Raw row {idx} - Names: {names}, Phone: {phone}")
            except Exception as e:
                logger.warning(f"Could not log row {idx}: {str(e)}")

        # Forward fill
        df["Names"] = df["Names"].ffill().astype(str)
        df["Phone"] = df["Phone"].ffill().astype(str)
        logger.info("Completed forward fill for Names and Phone columns")

        # Select required columns
        required_cols = ["Names", "Phone"]
        if "Room" in df.columns:
            required_cols.append("Room")
        df = df[required_cols]
        logger.info(f"Selected columns: {', '.join(required_cols)}")

        # Remove null rows
        initial_rows = len(df)
        df = df[df["Names"].notnull() & df["Phone"].notnull()]
        removed_rows = initial_rows - len(df)
        logger.info(f"Removed {removed_rows} rows with null values")

        # Log final preprocessed data
        logger.info(f"=== Preprocessing Complete: {len(df)} rows remaining ===")
        logger.info("Final preprocessed data:")
        for idx, row in df.iterrows():
            try:
                names = str(row['Names']) if pd.notna(row['Names']) else 'NULL'
                phone = str(row['Phone']) if pd.notna(row['Phone']) else 'NULL'
                logger.info(f"Preprocessed row {idx} - Names: {names}, Phone: {phone}")
            except Exception as e:
                logger.warning(f"Could not log row {idx}: {str(e)}")

        return df

    except Exception as e:
        logger.error(f"Error in preprocessing Excel: {str(e)}")
        raise

def clean_json_response(response: str) -> str:
    '''
    Clean the JSON response from the LLM by extracting only the JSON array part.
    Handles responses that might include explanatory text before or after the JSON.
    '''
    # Find the JSON array portion between brackets
    try:
        # Find the start and end of the JSON array
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON array found in response")

        # Extract just the JSON array part
        json_str = response[start_idx:end_idx]

        # Clean up any remaining markdown markers
        json_str = re.sub(r'```json|```', '', json_str)

        return json_str.strip()
    except Exception as e:
        logger.error(f"Error cleaning JSON response: {str(e)}")
        logger.error(f"Original response: {response}")
        raise

def process_contacts_bulk(df):
    '''
    Process all contacts in bulk with a single API call.
    '''
    logger.info("=== Starting Bulk Contact Processing ===")
    try:
        # Create contacts list from all rows
        contacts_list = []
        for idx, row in df.iterrows():
            try:
                name = str(row["Names"]).strip()
                phone = str(row["Phone"]).strip()
                contacts_list.append(f"Name: {name}, Phone: {phone}")
                logger.info(f"Raw contact {idx}: Name: {name}, Phone: {phone}")
            except Exception as e:
                logger.warning(f"Could not process row {idx}: {str(e)}")

        logger.info(f"Prepared {len(contacts_list)} contacts for processing")

        # Create batch data string
        batch_data = "\n".join(contacts_list)

        # Get prompts
        cnt_prompt = bulk_content_prompt(batch_data)
        sys_prompt = system_prompt()

        # Log complete LLM input
        logger.info("=== LLM Request Details ===")
        logger.info(f"System Prompt:\n{sys_prompt}")
        logger.info(f"Content Prompt:\n{cnt_prompt}")

        # Make API call
        logger.info(f"Sending batch prompt to OpenAI API with {len(contacts_list)} contacts")
        response = model_wrapper.single_shot_completion(
            system_prompt=sys_prompt,
            content_prompt=cnt_prompt,
            temperature=0.1
        )

        # Log complete response
        logger.info("=== LLM Response ===")
        logger.info(f"Raw LLM Response:\n{response}")

        try:
            # Clean the response before parsing
            cleaned_response = clean_json_response(response)
            logger.info(f"Cleaned Response for parsing:\n{cleaned_response}")

            cleaned_contacts = json.loads(cleaned_response)
            if not isinstance(cleaned_contacts, list):
                raise ValueError("LLM response is not a list of contacts")

            logger.info(f"Successfully parsed {len(cleaned_contacts)} contacts from LLM response")

            # Process valid contacts
            valid_contacts = []
            invalid_count = 0

            for idx, contact in enumerate(cleaned_contacts):
                try:
                    name = contact.get("name", "").strip()
                    phone = contact.get("phone", "").strip()

                    if name and phone:
                        phone = standardize_phone(phone)
                        if is_valid_phone(phone):
                            valid_contacts.append({"name": name, "phone": phone})
                            logger.info(f"Valid contact {idx} - Name: {name}, Phone: {phone}")
                        else:
                            logger.warning(f"Invalid contact {idx} - Name: {name}, Phone: {phone}")
                            invalid_count += 1
                    else:
                        logger.warning(f"Skipped empty contact {idx}")
                        invalid_count += 1
                except Exception as e:
                    logger.warning(f"Error processing contact {idx}: {str(e)}")
                    invalid_count += 1

            if not valid_contacts:
                logger.warning("No valid contacts found in LLM response")
                raise ValueError("No valid contacts found in LLM response")

            logger.info(f"=== Bulk Processing Complete ===")
            logger.info(f"- Total contacts processed: {len(cleaned_contacts)}")
            logger.info(f"- Valid contacts: {len(valid_contacts)}")
            logger.info(f"- Invalid contacts: {invalid_count}")

            return valid_contacts

        except json.JSONDecodeError as je:
            logger.error("Failed to parse LLM response as JSON:")
            logger.error(f"Error: {str(je)}")
            logger.error(f"Full response: {response}")
            raise

    except Exception as e:
        logger.error(f"Error in bulk processing: {str(e)}")
        logger.info("Falling back to manual cleaning")

        fallback_contacts = []
        skipped_count = 0

        for idx, row in df.iterrows():
            try:
                name = str(row["Names"]).strip()
                phone = str(row["Phone"]).strip()

                cleaned_name, cleaned_phone = manual_clean_contact(name, phone)
                if is_valid_phone(cleaned_phone):
                    fallback_contacts.append({
                        "name": cleaned_name,
                        "phone": cleaned_phone
                    })
                    logger.info(f"Manually cleaned contact {idx} - Name: {cleaned_name}, Phone: {cleaned_phone}")
                else:
                    skipped_count += 1
                    logger.info(f"Skipped invalid contact {idx} - Name: {cleaned_name}, Phone: {cleaned_phone}")

            except Exception as row_error:
                logger.warning(f"Could not clean row {idx}: {str(row_error)}")
                skipped_count += 1

        logger.info(f"Manual cleaning complete: {len(fallback_contacts)} valid contacts, {skipped_count} skipped")
        return fallback_contacts

def manual_clean_contact(raw_name, raw_phone):
    '''
    A fallback function to manually clean a contact.
    '''
    logger.info(f"Manual cleaning for: {raw_name}, {raw_phone}")
    cleaned_name = re.sub(r"\b(Mr\.|Ms\.|Mrs\.)\s*", "", raw_name, flags=re.IGNORECASE).strip()
    cleaned_phone = raw_phone.strip()
    cleaned_phone = standardize_phone(cleaned_phone)
    return cleaned_name, cleaned_phone

def format_name(name):
    '''
    Format the contact name to ensure that its length does not exceed 20 characters.
    If the name exceeds 20 characters, then replace the last name with just its first letter.
    '''
    if len(name) <= 20:
        return name
    parts = name.split()
    if len(parts) < 2:
        return name[:20]
    candidate = " ".join(parts[:-1] + [parts[-1][0]])
    if len(candidate) <= 20:
        return candidate
    else:
        return candidate[:20]

def generate_vcard(name, phone):
    '''
    Generate a vCard entry for a given contact.
    '''
    formatted_name = format_name(name)
    vcard = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"FN:{formatted_name}\n"
        f"TEL:{phone}\n"
        "END:VCARD\n"
    )
    logger.debug(f"Generated vCard for: {formatted_name}, {phone}")
    return vcard

def generate_summary(df):
    '''
    Generate a summary from the cleaned contacts DataFrame.
    This function uses the batch processed data.
    '''
    logger.info("Generating summary from batch processed data.")
    total_rows = len(df)
    contacts_summary = df.to_dict("records")
    valid_contacts = [(row["name"], row["phone"]) for row in contacts_summary if row["phone"] != "Missing" and is_valid_phone(row["phone"])]
    total_valid = len(valid_contacts)
    phone_list = [phone for _, phone in valid_contacts]
    unique_phones = set(phone_list)
    unique_count = len(unique_phones)

    duplicate_summary = {}
    non_unique_contacts = []
    for phone, count in Counter(phone_list).items():
        if count > 1:
            names = [name for name, p in valid_contacts if p == phone]
            duplicate_summary[phone] = {"first_name": names[0], "duplicates": names[1:]}
            non_unique_contacts.extend(names)
    non_unique_contacts = list(set(non_unique_contacts))

    seen = {}
    final_contacts = []
    for entry in contacts_summary:
        phone = entry["phone"]
        name = entry["name"]
        if phone != "Missing":
            if phone not in seen:
                final_contacts.append({"name": name, "phone": phone})
                seen[phone] = 1
            else:
                final_contacts.append({"name": name, "phone": "Missing"})
                seen[phone] += 1
        else:
            final_contacts.append({"name": name, "phone": "Missing"})

    different_area_codes = []
    for name, phone in valid_contacts:
        if not is_turkish_mobile(phone):
            different_area_codes.append({"name": name, "phone": phone})

    summary = {
        "total_rows": total_rows,
        "total_valid_contacts": total_valid,
        "unique_phone_numbers": unique_count,
        "total_rooms": 0,  # This could be updated if room information is needed
        "missing_phone_numbers": [entry["name"] for entry in final_contacts if entry["phone"] == "Missing"],
        "duplicate_phone_numbers": duplicate_summary,
        "non_unique_contacts": non_unique_contacts,
        "unique_contacts": final_contacts,
        "different_area_codes": different_area_codes
    }
    logger.info("Summary generated successfully.")
    return summary

def is_valid_phone(phone):
    '''
    Check if the phone number is valid.
    A valid phone should be in the format: +90 followed by exactly 10 digits.
    '''
    return bool(re.fullmatch(r"\+90\d{10}", phone))

def is_valid_name(name):
    '''
    Check if the name is valid.
    A valid name should contain at least two words and not contain irrelevant keywords.
    '''
    if len(name.split()) < 2:
        return False
    irrelevant_keywords = ["hotel", "flight", "brickell", "address", "conference", "airport", "vouchers", "group"]
    for keyword in irrelevant_keywords:
        if keyword in name.lower():
            return False
    return True

def is_valid_contact(name, phone):
    '''
    Check if the contact is valid by ensuring both the name and phone number meet validation criteria.
    '''
    return is_valid_phone(phone) and is_valid_name(name)

def parse_excel(file):
    '''
    Parse and process the Excel file using batch processing.
    Returns a DataFrame of cleaned contacts with columns "name" and "phone".
    '''
    logger.info("Starting Excel parsing for batch processing.")
    try:
        df_raw = preprocess_excel(file)
        cleaned_contacts = process_contacts_bulk(df_raw)
        result_df = pd.DataFrame(cleaned_contacts)
        logger.info(f"Successfully processed {len(result_df)} contacts in bulk.")
        return result_df
    except Exception as e:
        logger.error(f"Error in parse_excel: {str(e)}")
        raise