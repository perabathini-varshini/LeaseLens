from src.text_cleaner import clean_text


messy_text = """
    
    
    2. RENT    
    
    
    The Tenant     shall pay a monthly rent of INR 50,000.
    
    
    Rent shall be paid on or before the 5th day of each month.
    
    
"""


print("BEFORE CLEANING")
print("=" * 60)
print(messy_text)


cleaned_text = clean_text(messy_text)


print("\nAFTER CLEANING")
print("=" * 60)
print(cleaned_text)