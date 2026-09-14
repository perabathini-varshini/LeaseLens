import re


# ---------------------------------------------------------
# Numbered section pattern
# Examples:
# 1. PARTIES
# 2. RENT
# 3. SECURITY DEPOSIT
# ---------------------------------------------------------

NUMBERED_SECTION_PATTERN = re.compile(
    r"^\s*(\d+)\.\s+(.+?)\s*$"
)


# ---------------------------------------------------------
# Known lease section headings
# ---------------------------------------------------------

KNOWN_SECTION_TITLES = {
    "PARTIES",
    "PARTIES AND PREMISES",
    "TERM OF LEASE",
    "RENT",
    "MONTHLY RENT",
    "SECURITY DEPOSIT",
    "MAINTENANCE",
    "REPAIRS AND MAINTENANCE",
    "USE OF PREMISES",
    "TERMINATION",
    "TERMINATION AND NOTICE",
    "GOVERNING LAW",
}


# ---------------------------------------------------------
# Document titles that must NOT become sections
# ---------------------------------------------------------

DOCUMENT_TITLES = {
    "LEASE AGREEMENT",
    "RESIDENTIAL LEASE AGREEMENT",
    "COMMERCIAL LEASE AGREEMENT",
    "RENTAL AGREEMENT",
    "RESIDENTIAL RENTAL AGREEMENT",
}


def detect_sections(documents: list[dict]) -> list[dict]:

    sections = []

    current_section = None
    auto_section_number = 0

    for document in documents:

        text = document["text"].strip()

        if not text:
            continue

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            normalized = re.sub(r"\s+", " ", line).strip()
            upper_line = normalized.upper()

            # -------------------------------------------------
            # 1. Check numbered section
            # -------------------------------------------------

            numbered_match = NUMBERED_SECTION_PATTERN.match(normalized)

            if numbered_match:

                # Store previous section
                if current_section is not None:

                    current_section["text"] = "\n".join(
                        current_section["text"]
                    ).strip()

                    sections.append(current_section)

                section_number = int(numbered_match.group(1))
                title = numbered_match.group(2).strip()

                current_section = {
                    "section_number": section_number,
                    "title": title,
                    "text": [],
                    "source": document["source"],
                    "location": document["location"],
                    "location_type": document["location_type"]
                }

                continue

            # -------------------------------------------------
            # 2. Ignore document titles
            # -------------------------------------------------

            if upper_line in DOCUMENT_TITLES:
                continue

            # -------------------------------------------------
            # 3. Check known lease section headings
            # -------------------------------------------------

            if upper_line in KNOWN_SECTION_TITLES:

                # Store previous section
                if current_section is not None:

                    current_section["text"] = "\n".join(
                        current_section["text"]
                    ).strip()

                    sections.append(current_section)

                auto_section_number += 1

                current_section = {
                    "section_number": auto_section_number,
                    "title": normalized,
                    "text": [],
                    "source": document["source"],
                    "location": document["location"],
                    "location_type": document["location_type"]
                }

                continue

            # -------------------------------------------------
            # 4. Normal content belongs to current section
            # -------------------------------------------------

            if current_section is not None:
                current_section["text"].append(normalized)

    # ---------------------------------------------------------
    # Store final section
    # ---------------------------------------------------------

    if current_section is not None:

        current_section["text"] = "\n".join(
            current_section["text"]
        ).strip()

        sections.append(current_section)

    return sections