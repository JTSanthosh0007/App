import pandas as pd
import pdfplumber
from pathlib import Path
import io
import re
from datetime import datetime
import json
import sys
import argparse
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatementParser:
    def __init__(self, file_source):
        # file_source can be a file path (string or Path object) or a file-like object
        self.file_source = file_source
        self.filename = getattr(file_source, 'name', 'uploaded_file') # Get name if file object
        logger.info(f"Initializing parser for file: {self.filename}")

    def parse(self):
        """Parse the file into a standardized DataFrame"""
        try:
            if isinstance(self.file_source, (str, Path)):
                if str(self.file_source).endswith('.pdf'):
                    logger.info(f"Opening PDF file: {self.file_source}")
                    return self._parse_pdf(open(self.file_source, 'rb'))
                else:
                    raise ValueError("Unsupported file format")
            elif hasattr(self.file_source, 'read'): # Check if it's a file-like object
                logger.info("Processing file-like object")
                return self._parse_pdf(self.file_source)
            else:
                raise ValueError("Unsupported file source type")
        except Exception as e:
            logger.error(f"Error in parse method: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _parse_pdf(self, pdf_file_obj):
        """Handle PDF parsing with comprehensive extraction"""
        try:
            with pdfplumber.open(pdf_file_obj) as pdf:
                all_extracted_text = []
                logger.info(f"PDF opened successfully. Number of pages: {len(pdf.pages)}")
                
                # Transaction patterns for PhonePe statements
                transaction_patterns = [
                    # Pattern 1: PhonePe standard format
                    re.compile(
                        r'(?P<date>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},\s*\d{4})\s*'
                        r'(?P<time>\d{2}:\d{2}\s*[AP]M)?\s*'
                        r'(?P<description>.*?)\s*'
                        r'(?P<type>Credit|Debit)?\s*'
                        r'(?:INR|₹|Rs\.?)\s*(?P<amount>[\d,]+\.?\d*)',
                        re.IGNORECASE | re.MULTILINE | re.DOTALL
                    ),
                    # Pattern 2: Alternative PhonePe format
                    re.compile(
                        r'(?P<date>\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4})\s*'
                        r'(?P<time>\d{2}:\d{2}\s*[AP]M)?\s*'
                        r'(?P<description>.*?)\s*'
                        r'(?P<amount>[-+]?₹?\s*[\d,]+\.?\d*)',
                        re.IGNORECASE | re.MULTILINE | re.DOTALL
                    )
                ]

                # Extract text from all pages
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        all_extracted_text.append(text)
                        logger.debug(f"Extracted text from page {i+1}")

                full_text = "\n".join(all_extracted_text)
                transactions = []
                logger.info("Starting transaction extraction")

                # Extract transactions
                for pattern in transaction_patterns:
                    matches = list(pattern.finditer(full_text))
                    logger.info(f"Found {len(matches)} potential transactions with pattern")
                    
                    for match in matches:
                        try:
                            date_str = match.group('date').strip()
                            date = self._parse_date(date_str)
                            description = match.group('description').strip()
                            amount_str = match.group('amount')
                            amount_str = re.sub(r'[₹,\s]', '', amount_str)
                            amount = float(amount_str)
                            
                            transaction_type = match.group('type') if 'type' in match.groupdict() else None
                            if transaction_type:
                                transaction_type = transaction_type.upper()
                                if transaction_type in ['DEBIT', 'Dr']:
                                    amount = -abs(amount)
                            
                            transactions.append({
                                'date': date,
                                'amount': amount,
                                'description': description,
                                'category': self._categorize_transaction(description)
                            })
                            logger.debug(f"Processed transaction: {date} - {amount} - {description}")
                        except Exception as e:
                            logger.warning(f"Could not process transaction: {e}")
                            logger.debug(f"Problematic match: {match.groupdict()}")

                if transactions:
                    logger.info(f"Successfully extracted {len(transactions)} transactions")
                    df = pd.DataFrame(transactions)
                    df = df[df['amount'].abs() > 0]
                    df = df.drop_duplicates(subset=['date', 'amount', 'description'])
                    df = df.sort_values('date')
                    return df
                else:
                    logger.warning("No transactions found in the PDF")
                    return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            logger.error(traceback.format_exc())
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

    def _parse_date(self, date_str):
        """Parse date string into datetime object"""
        try:
            if not date_str:
                return datetime.now()

            date_str = date_str.strip()
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
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    if parsed_date.year > datetime.now().year:
                        parsed_date = parsed_date.replace(year=datetime.now().year)
                    return parsed_date
                except ValueError:
                    continue
            
            # Fallback: try to extract components
            components = re.findall(r'\d+', date_str)
            if len(components) >= 3:
                day, month, year = map(int, components[:3])
                if year < 100:
                    year += 2000 if year < 50 else 1900
                return datetime(year, month, day)
            
            return datetime.now()
            
        except Exception as e:
            logger.error(f"Date parsing error: {str(e)}")
            return datetime.now()

    def _categorize_transaction(self, description):
        """Categorize transaction based on description"""
        description = description.lower()
        
        categories = {
            'Food': ['restaurant', 'food', 'swiggy', 'zomato', 'dining'],
            'Transportation': ['uber', 'ola', 'metro', 'fuel', 'petrol', 'diesel'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'retail', 'store'],
            'Bills': ['electricity', 'water', 'gas', 'mobile', 'internet', 'broadband'],
            'Entertainment': ['movie', 'netflix', 'amazon prime', 'hotstar'],
            'Transfer': ['transfer', 'sent', 'received', 'upi', 'neft', 'imps'],
            'Salary': ['salary', 'income', 'payment'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        
        return 'Others'

def parse_statement_from_file(file_source):
    """Function to parse a statement from a file-like object or path."""
    statement_parser = StatementParser(file_source)
    df = statement_parser.parse()
    
    # Convert DataFrame to dictionary format
    transactions = []
    for _, row in df.iterrows():
        transactions.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'amount': float(row['amount']),
            'description': str(row['description']) if 'description' in row else '',
            'category': str(row['category'])
        })

    # Calculate totals
    total_received = float(df[df['amount'] > 0]['amount'].sum())
    total_spent = float(df[df['amount'] < 0]['amount'].sum())
    
    # Calculate category breakdown
    category_breakdown = df[df['amount'] < 0].groupby('category')['amount'].sum().to_dict()
    category_breakdown = {k: float(v) for k, v in category_breakdown.items()}

    # Create response object
    response = {
        'transactions': transactions,
        'totalReceived': total_received,
        'totalSpent': total_spent,
        'categoryBreakdown': category_breakdown
    }
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse bank statements')
    parser.add_argument('file_path', help='Path to the PDF statement file')
    args = parser.parse_args()

    try:
        results = parse_statement_from_file(args.file_path)
        print(json.dumps(results))
        sys.exit(0)
    except Exception as e:
        error_response = {'error': str(e)}
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1) 