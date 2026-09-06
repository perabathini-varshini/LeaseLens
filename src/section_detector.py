import re


SECTION_PATTERN = re.compile(
    r"^\s*(\d+)\.\s+(.+?)\s*$"
)


def detect_sections(documents: list[dict]) -> list[dict]:
    """
    Detect numbered sections from normalized documents.

    Example:
        1. PARTIES
        2. RENT
        3. SECURITY DEPOSIT
    """

    sections = []

    current_section = None

    for document in documents:

        text = document["text"].strip()

        if not text:
            continue

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            match = SECTION_PATTERN.match(line)

            if match:

                # Store previous section
                if current_section is not None:

                    current_section["text"] = "\n".join(
                        current_section["text"]
                    ).strip()

                    sections.append(current_section)

                # Extract heading information
                section_number = int(match.group(1))
                title = match.group(2).strip()

                current_section = {
                    "section_number": section_number,
                    "title": title,
                    "text": [],
                    "source": document["source"],
                    "location": document["location"],
                    "location_type": document["location_type"]
                }

            else:

                # Add content to current section
                if current_section is not None:

                    current_section["text"].append(line)

    # Store final section
    if current_section is not None:

        current_section["text"] = "\n".join(
            current_section["text"]
        ).strip()

        sections.append(current_section)

    return sections