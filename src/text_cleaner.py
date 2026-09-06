import re


def clean_text(text: str) -> str:
    """
    Clean formatting noise from extracted document text.

    The actual legal wording is preserved.
    """

    if not text:
        return ""

    # Replace Windows-style line endings
    text = text.replace("\r\n", "\n")

    # Replace remaining carriage returns
    text = text.replace("\r", "\n")

    # Remove spaces at the beginning/end of each line
    lines = []

    for line in text.split("\n"):

        cleaned_line = line.strip()

        if cleaned_line:
            lines.append(cleaned_line)

    # Rebuild the text
    text = "\n".join(lines)

    # Reduce multiple spaces to one
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()