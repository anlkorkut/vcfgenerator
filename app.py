'''
app.py code file.
'''

import streamlit as st
from logger import init
from apps.vcfgenerator.utils import (
  parse_excel,
  generate_summary,
  generate_vcard,
  is_valid_contact
)
from apps.vcfgenerator.email_utils import send_missing_contacts_email
import logging

logger = logging.getLogger(__name__)

# Clear any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Initialize logger
logger = init(__name__)

# Optional: Add DuplicateFilter if still needed
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

if not any(isinstance(f, DuplicateFilter) for f in logger.filters):
    logger.addFilter(DuplicateFilter())

def main():
    logger.info("Application started.")
    st.title("Excel to VCF Converter with AI Data Cleaning & Summary")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        logger.info("File uploaded successfully.")

        with st.spinner("Parsing Excel file..."):
            try:
                cleaned_df = parse_excel(uploaded_file)
                logger.info(f"Batch processed contacts: {len(cleaned_df)} records.")
            except Exception as e:
                logger.error(f"Error parsing Excel file: {e}")
                st.error("Error parsing Excel file.")
                return

        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)

        with st.spinner("Generating summary..."):
            try:
                summary = generate_summary(cleaned_df)
                logger.info("Generated summary successfully.")

                # Display metrics in columns
                with col1:
                    st.metric(
                        label="Total Valid Contacts",
                        value=summary['total_valid_contacts']
                    )

                with col2:
                    st.metric(
                        label="Total Rows in Excel",
                        value=summary['total_rows']
                    )

                with col3:
                    st.metric(
                        label="Unique Phone Numbers",
                        value=summary['unique_phone_numbers']
                    )
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                st.error("Error generating summary.")
                return

        st.subheader("Data Preview")
        st.dataframe(cleaned_df)
        logger.info("Displayed data preview.")

        with st.spinner("Generating VCF file..."):
            vcf_entries = []
            used_phone_numbers = set()

            for _, row in cleaned_df.iterrows():
                name = row["name"]
                phone = row["phone"]

                if phone == "Missing" or phone in used_phone_numbers:
                    continue

                if is_valid_contact(name, phone):
                    used_phone_numbers.add(phone)
                    vcard = generate_vcard(name, phone)
                    vcf_entries.append(vcard)

            if vcf_entries:
                vcf_content = "\n".join(vcf_entries)
                st.download_button(
                    label="Download VCF",
                    data=vcf_content,
                    file_name="contacts.vcf",
                    mime="text/vcard",
                    use_container_width=True
                )
                logger.info("VCF file generated successfully.")
            else:
                st.error("No valid contacts found to generate VCF.")
                logger.error("No valid contacts found to generate VCF.")

        st.write("---")

        # Restore expandable sections
        with st.expander("Valid Contacts", expanded=True):
            if summary["unique_contacts"]:
                contacts_with_phone = [entry for entry in summary["unique_contacts"] if entry["phone"] != "Missing"]
                contacts_without_phone = [entry for entry in summary["unique_contacts"] if entry["phone"] == "Missing"]

                col_valid, col_missing = st.columns(2)

                with col_valid:
                    st.markdown("**Contacts with Numbers:**")
                    for entry in contacts_with_phone:
                        st.markdown(f"- **{entry['name']}**: <a href='tel:{entry['phone']}'>{entry['phone']}</a>", unsafe_allow_html=True)

                with col_missing:
                    st.markdown("**Contacts without Numbers:**")
                    for entry in contacts_without_phone:
                        st.markdown(f"- **{entry['name']}**: Missing", unsafe_allow_html=True)

                    if contacts_without_phone:
                        if st.button("Email Missing Contacts List"):
                            missing_names = [entry['name'] for entry in contacts_without_phone]
                            success, message = send_missing_contacts_email(missing_names)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

        with st.expander("Duplicate Numbers", expanded=False):
            if summary["duplicate_phone_numbers"]:
                for phone, info in summary["duplicate_phone_numbers"].items():
                    st.write(f"**{phone}**")
                    st.write(f"- First: {info['first_name']}")
                    st.write(f"- Duplicates: {', '.join(info['duplicates'])}")
            else:
                st.write("No duplicate numbers found.")

if __name__ == "__main__":
    main()
    logger.info("Application finished execution.")