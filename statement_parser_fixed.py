import pandas as pd
import plotly.express as px
import pdfplumber
from pathlib import Path
import io
import streamlit as st
import re
from pdfminer.layout import LAParams
import PyPDF2
import fitz  #  PyMuPDF
import traceback  # Import traceback for detailed error logging
import logging  # Import logging for error handling
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatementParser:
    def __init__(self, file_obj):
        if file_obj is None:
            raise ValueError("File object cannot be None")
        if not hasattr(file_obj, 'read'):
            raise ValueError("File object must have a read method")
        if not hasattr(file_obj, 'name'):
            raise ValueError("File object must have a name attribute")
            
        self.file_obj = file_obj
        self.transactions = []
        
    def parse(self):
        try:
            if self.file_obj.name.endswith('.pdf'):
                return self._parse_pdf()
            else:
                raise ValueError("Unsupported file format. Only PDF files are supported.")
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _parse_pdf(self):
        try:
            pdf_stream = io.BytesIO(self.file_obj.read())
            
            # Check if file is empty
            if pdf_stream.getbuffer().nbytes == 0:
                st.error("The uploaded file is empty.")
                return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
            
            # Check file size (limit to 50MB)
            if pdf_stream.getbuffer().nbytes > 50 * 1024 * 1024:  # 50MB in bytes
                st.error("File size exceeds 50MB limit. Please upload a smaller file.")
                return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
            
            with pdfplumber.open(pdf_stream) as pdf:
                # Check if PDF has pages
                if len(pdf.pages) == 0:
                    st.error("The PDF file contains no pages.")
                    return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
                
                # Enhanced debugging: Log total pages and initial text extraction
                st.write(f"Total PDF Pages: {len(pdf.pages)}")
                
                all_extracted_text = []
                parsing_errors = []
                
                # Process pages in chunks to manage memory
                chunk_size = 10  # Process 10 pages at a time
                for i in range(0, len(pdf.pages), chunk_size):
                    chunk = pdf.pages[i:i + chunk_size]
                    for page_num, page in enumerate(chunk, i + 1):
                        try:
                            text = page.extract_text(
                                x_tolerance=3,
                                y_tolerance=3,
                                layout=True,
                                keep_blank_chars=False
                            )

                            if text and text.strip():
                                all_extracted_text.append(text)
                        
                        except Exception as e:
                            logger.error(f"Text extraction error on page {page_num}: {e}")
                            parsing_errors.append(f"Page {page_num}: {str(e)}")
                    
                    # Clear memory after each chunk
                    del chunk
                
                # Combine all extracted text
                full_text = "\n".join(all_extracted_text)
                
                # Ultra-flexible transaction extraction patterns
                transaction_patterns = [
                    # Pattern 1: Comprehensive format with multiple variations
                    re.compile(
                        r'(?P<date>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},\s*\d{4})\s*'
                        r'(?P<description>.*?)'
                        r'(?P<type>DEBIT|CREDIT|Dr|Cr)?\s*'
                        r'(?:₹|Rs\.?)\s*(?P<amount>[\d,]+\.?\d*)',
                        re.IGNORECASE | re.MULTILINE | re.DOTALL
                    ),
                    
                    # Pattern 2: More relaxed matching
                    re.compile(
                        r'(?P<date>\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4})\s*'
                        r'(?P<description>.*?)'
                        r'(?P<amount>[-+]?₹?\s*[\d,]+\.?\d*)',
                        re.IGNORECASE | re.MULTILINE | re.DOTALL
                    )
                ]

                # Extract transactions from full text
                transactions = []
                for pattern in transaction_patterns:
                    for match in pattern.finditer(full_text):
                        try:
                            # Parse date with multiple strategies
                            date_str = match.group('date').strip()
                            date = self._parse_date(date_str)
                            
                            # Parse description
                            description = match.group('description').strip()
                            
                            # Parse amount with multiple cleaning strategies
                            amount_str = match.group('amount')
                            amount_str = re.sub(r'[₹,\s]', '', amount_str)
                            amount = float(amount_str)
                            
                            # Determine transaction type
                            transaction_type = match.group('type') if 'type' in match.groupdict() else None
                            if transaction_type:
                                transaction_type = transaction_type.upper()
                            else:
                                transaction_type = 'CREDIT' if amount > 0 else 'DEBIT'
                            
                            # Adjust amount based on transaction type
                            if transaction_type == 'DEBIT' or transaction_type == 'Dr':
                                amount = -abs(amount)
                            
                            # Append transaction
                            transactions.append({
                                'date': date,
                                'amount': amount,
                                'description': description,
                                'category': self._categorize_transaction(description)
                            })
                        
                        except Exception as e:
                            logger.warning(f"Could not process transaction: {e}")

                # Create DataFrame
                if transactions:
                    df = pd.DataFrame(transactions)
                    
                    # Advanced validation and cleaning
                    df = df[df['amount'].abs() > 0]  # Remove zero or near-zero amount transactions
                    df = df.drop_duplicates(subset=['date', 'amount', 'description'])  # Remove exact duplicates
                    df = df.sort_values('date')  # Sort by date
                    
                    st.success(f"Successfully extracted {len(df)} transactions.")
                    return df
                else:
                    st.error("No transactions could be extracted.")
                    st.write("Extracted Text Debugging:", full_text[:1000])
                    return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _parse_date(self, date_str):
        try:
            # Normalize the date string
            if not date_str:
                logger.warning(f"Empty date string received")
                return datetime.now()

            date_str = date_str.strip()
            
            # Extensive logging for debugging
            logger.info(f"Attempting to parse date string: '{date_str}'")
            
            # Date formats to try (most specific to least specific)
            date_formats = [
                '%d %b %Y',      # 06 Nov 2024
                '%b %d %Y',      # Nov 06 2024
                '%d %B %Y',      # 06 November 2024
                '%B %d %Y',      # November 06 2024
                '%m/%d/%Y',      # 11/06/2024
                '%d/%m/%Y',      # 06/11/2024
                '%Y-%m-%d',      # 2024-11-06
                '%d-%m-%Y',      # 06-11-2024
                '%b %d, %Y',     # Nov 06, 2024
                '%d %b, %Y',     # 06 Nov, 2024
                '%d-%b-%Y',      # 06-Nov-2024
                '%b-%d-%Y'       # Nov-06-2024
            ]
            
            # Try parsing with different formats
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    
                    # Handle future dates
                    current_year = datetime.now().year
                    if parsed_date.year > current_year:
                        # Adjust to current or previous year
                        parsed_date = parsed_date.replace(year=current_year)
                    
                    logger.info(f"Successfully parsed date: {parsed_date}")
                    return parsed_date
                except ValueError as ve:
                    # Log specific format failure
                    logger.debug(f"Failed to parse with format {fmt}: {ve}")
                    continue
            
            # Fallback parsing with more flexible approach
            try:
                # Extract numeric components
                components = re.findall(r'\d+', date_str)
                
                if len(components) >= 3:
                    # Try different component orders
                    possible_orders = [
                        (components[0], components[1], components[2]),  # day, month, year
                        (components[1], components[0], components[2]),  # month, day, year
                        (components[2], components[0], components[1])   # year, day, month
                    ]
                    
                    for day, month, year in possible_orders:
                        # Convert to integers
                        day, month, year = int(day), int(month), int(year)
                        
                        # Handle two-digit years
                        if year < 100:
                            year += 2000 if year < 50 else 1900
                        
                        try:
                            parsed_date = datetime(year, month, day)
                            
                            # Adjust future dates
                            current_year = datetime.now().year
                            if parsed_date.year > current_year:
                                parsed_date = parsed_date.replace(year=current_year)
                            
                            logger.info(f"Successfully parsed flexible date: {parsed_date}")
                            return parsed_date
                        except ValueError as ve:
                            logger.debug(f"Failed flexible parsing: {ve}")
                            continue
            except Exception as e:
                logger.error(f"Unexpected error in flexible date parsing: {e}")
            
            # If all parsing fails, log detailed warning and use current date
            logger.warning(f"Could not parse date: '{date_str}'. Original input: {repr(date_str)}")
            return datetime.now()
        
        except Exception as e:
            # Catch-all error handling
            logger.error(f"Critical error in date parsing: {e}")
            return datetime.now()

    def _categorize_transaction(self, description):
        description = description.lower()
        
        # Expanded and more nuanced categorization with weighted scoring
        categories = {
            'Family Support': {
                'keywords': [
                    'dad', 'mom', 'father', 'mother', 'parents', 'family', 'gift',
                    'brother', 'sister', 'sibling', 'son', 'daughter', 'child', 'children',
                    'wife', 'husband', 'spouse', 'partner',
                    'grandfather', 'grandmother', 'grandparents', 'uncle', 'aunt', 'cousin',
                    'nephew', 'niece', 'in-laws', 'mother-in-law', 'father-in-law',
                    'brother-in-law', 'sister-in-law', 'stepfather', 'stepmother', 
                    'stepbrother', 'stepsister', 'half-brother', 'half-sister', 
                    'godfather', 'godmother', 'godparent',
                    'home', 'household', 'guardian', 'caretaker', 'dependents', 'provider',
                    'breadwinner', 'foster parent', 'adoptive parent', 'caregiver', 'nanny',
                    'support', 'care', 'love', 'help', 'nurturing', 'protection', 'bonding', 
                    'guidance', 'responsibility', 'commitment', 'trust', 'unity', 'sacrifice', 
                    'loyalty', 'companionship', 'respect', 'devotion', 'understanding',
                    'anniversary', 'birthday', 'celebration', 'reunion', 'family gathering', 
                    'holiday', 'tradition', 'legacy', 'inheritance', 'heritage', 'roots',
                    'elders', 'relatives', 'upbringing', 'well-being', 'parenting', 'genealogy',
                    'lineage', 'descendants', 'heir', 'next of kin', 'family tree'
                ],
                'weight': 0.9
            },
            'Food': {
                'keywords': [
                    'restaurant', 'food', 'dining', 'cafe', 'hotel', 'meal', 'fast food', 'street food',
                    'buffet', 'takeaway', 'home delivery', 'drive-thru', 'fine dining', 'food truck',
                    'catering', 'brunch', 'lunch', 'dinner', 'breakfast', 'snacks', 'midnight snack',
                    'mcdonalds', 'kfc', 'dominos', 'pizza hut', 'burger king', 'subway', 'starbucks',
                    'dunkin donuts', 'hard rock cafe', 'taco bell', 'chipotle', 'wendys', 'panda express',
                    'krispy kreme', 'baskin robbins', 'five guys', 'carls jr', 'popeyes', "arby's", 'in-n-out',
                    'zomato', 'swiggy', 'ubereats', 'foodpanda', 'dunzo', 'grubhub', 'doordash', 
                    'postmates', 'deliveroo', 'just eat',
                    'cooking', 'baking', 'grilling', 'smoking meat', 'barbecue night', 'wine tasting', 
                    'food festival', 'street food tour', 'grocery shopping', 'meal prep', 'cake decorating', 
                    'pastry making', 'beer brewing', 'coffee roasting', 'home cooking', 'farm-to-table',
                    'food photography', 'food blogging', 'recipe testing', 'restaurant review',
                    'thanksgiving dinner', 'christmas feast', 'easter brunch', 'diwali sweets', 
                    'ramadan iftar', 'oktoberfest', 'chinese new year dinner', 'hanukkah feast', 
                    'halloween candy', 'mardi gras food', "valentine's day chocolates",
                    'grilling', 'frying', 'roasting', 'baking', 'steaming', 'boiling', 'sauteing',
                    'braising', 'stir-frying', 'poaching', 'slow cooking', 'deep frying', 'blanching',
                    'pickling', 'fermenting', 'canning',
                    'spices', 'herbs', 'salt', 'pepper', 'sugar', 'butter', 'oil', 'vinegar', 
                    'soy sauce', 'hot sauce', 'mayonnaise', 'mustard', 'ketchup', 'cheese', 
                    'yogurt', 'milk', 'cream', 'honey', 'flour', 'rice', 'pasta', 'bread', 'oats',
                    'lentils', 'beans', 'tofu', 'nuts', 'seeds', 'chocolate syrup',
                    'gluten-free', 'dairy-free', 'nut-free', 'low sugar', 'low sodium', 'vegetarian',
                    'vegan', 'pescatarian', 'halal', 'kosher',
                    'plating', 'garnishing', 'food styling', 'food photography', 'molecular gastronomy',
                    'gourmet', 'fine dining experience', 'fusion food',
                    'oven', 'stove', 'microwave', 'grill', 'air fryer', 'pressure cooker', 'blender', 
                    'mixer', 'whisk', 'spatula', 'knife', 'cutting board', 'baking tray', 'rolling pin',
                    'measuring cups', 'colander', 'peeler', 'food processor',
                    'freezing', 'refrigeration', 'vacuum sealing', 'pickling', 'drying', 'canning',
                    'smoking', 'fermenting',
                    'truffle', 'caviar', 'escargot', 'foie gras', 'shark fin soup', 'durian', 'kimchi',
                    'wasabi', 'black garlic', 'saffron', 'dragon fruit', 'jackfruit', 'quinoa', 'tempeh',
                    'miso', 'natto', 'blue cheese',
                    'spicy food challenge', 'mukbang', 'food ASMR', 'eating contest', 'cheeseburger challenge',
                    "world's largest pizza", 'one chip challenge',
                    'krabby patty', 'scooby snacks', 'chocolate frogs', 'butterbeer', 'turkish delight',
                    'waffles from stranger things', 'ramen from naruto', 'harry potter feast',
                    'poutine', 'haggis', 'pierogi', 'sauerbraten', 'ceviche', 'paella', 'baklava', 
                    'falafel', 'katsu', 'bobotie', 'cassava', 'jerk chicken', 'empanadas', 'gumbo'
                ],
                'weight': 0.8
            }
        }
        
        # Find the best matching category
        best_category = None
        best_score = 0
        
        for category, data in categories.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in description:
                    score += data['weight']
            
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category if best_category else 'Uncategorized' 