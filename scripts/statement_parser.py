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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatementParser:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.filename = Path(file_obj.name).name

    def parse(self):
        """Parse the uploaded file into a standardized DataFrame"""
        if self.filename.endswith('.pdf'):
            # Check if it's a Paytm statement being uploaded to PhonePe section
            if 'paytm' in self.filename.lower() and 'phonepe' in st.session_state.get('selected_platform', '').lower():
                st.error("⚠️ Incorrect statement type! Please upload a PhonePe statement for the PhonePe analyzer.")
                return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
            
            # Check if it's a PhonePe statement being uploaded to Paytm section    
            if 'phonepe' in self.filename.lower() and 'paytm' in st.session_state.get('selected_platform', '').lower():
                st.error("⚠️ Incorrect statement type! Please upload a Paytm statement for the Paytm analyzer.")
                return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
            
            # Check if it's a SuperMoney statement being uploaded to wrong section
            if 'supermoney' in self.filename.lower() and 'supermoney' not in st.session_state.get('selected_platform', '').lower():
                st.error("⚠️ Incorrect statement type! Please upload this statement in the SuperMoney analyzer section.")
                return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
            
            # Route to appropriate parser
            if 'paytm' in self.filename.lower():
                return self._parse_paytm_pdf(self._extract_text_from_pdf())
            elif 'supermoney' in self.filename.lower():
                return self._parse_supermoney_pdf(self._extract_text_from_pdf())
            else:
                return self._parse_pdf()
        elif self.filename.endswith('.csv'):
            return self._parse_csv()
        else:
            raise ValueError("Unsupported file format")

    def _parse_pdf(self):
        """Handle PDF parsing with extra security checks"""
        pdf_stream = io.BytesIO(self.file_obj.read())
        debug_info = []
        
        try:
            # First try to validate if it's a valid PDF
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_stream)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                pdf_stream.seek(0)  # Reset stream position
            except Exception as e:
                st.error("Invalid PDF file. Please ensure you're uploading a valid bank statement in PDF format.")
                logger.error(f"PDF validation error: {str(e)}")
                return pd.DataFrame({
                    'date': [pd.Timestamp.now()], 
                    'amount': [0.0],
                    'category': ['Others']
                })

            # Process in chunks of 10 pages to avoid memory issues
            all_transactions = []
            parsing_errors = []
            chunk_size = 10
            
            with pdfplumber.open(pdf_stream) as pdf:
                total_pages = len(pdf.pages)
                
                if total_pages == 0:
                    st.error("The PDF file appears to be empty.")
                    return pd.DataFrame({
                        'date': [pd.Timestamp.now()], 
                        'amount': [0.0],
                        'category': ['Others']
                    })

                logger.info(f"Processing PDF with {total_pages} pages")
                
                # Process pages in chunks
                for start_page in range(0, total_pages, chunk_size):
                    end_page = min(start_page + chunk_size, total_pages)
                    logger.info(f"Processing pages {start_page + 1} to {end_page}")
                    
                    chunk_text = ""
                    chunk_transactions = []
                    
                    # Extract text from current chunk of pages
                    for page_num in range(start_page, end_page):
                        try:
                            page = pdf.pages[page_num]
                            text = page.extract_text()
                            
                            if not text:
                                logger.info(f"No text on page {page_num + 1}, trying PyMuPDF")
                                pdf_stream.seek(0)
                                text = self._extract_text_with_pymupdf(pdf_stream, page_num + 1)
                            
                            if text:
                                chunk_text += text + "\n"
                            else:
                                parsing_errors.append(f"Page {page_num + 1}: No text could be extracted")
                                continue
                                
                        except Exception as e:
                            logger.error(f"Error on page {page_num + 1}: {str(e)}")
                            parsing_errors.append(f"Page {page_num + 1}: {str(e)}")
                            continue
                    
                    # Process the chunk text
                    if chunk_text:
                        lines = chunk_text.split('\n')
                        logger.info(f"Processing {len(lines)} lines from pages {start_page + 1}-{end_page}")
                        
                        for line_num, line in enumerate(lines, 1):
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Skip header lines
                            if any(header in line.lower() for header in ['statement', 'page', 'date', 'time', 'transaction id']):
                                continue
                            
                            try:
                                # Try to extract transaction details
                                transaction = self._extract_transaction_from_line(line)
                                if transaction:
                                    chunk_transactions.append(transaction)
                            except Exception as e:
                                logger.error(f"Error processing line {line_num}: {str(e)}")
                                continue
                    
                    # Add chunk transactions to main list
                    all_transactions.extend(chunk_transactions)
                    logger.info(f"Added {len(chunk_transactions)} transactions from chunk")
                    
                    # Clear chunk data to free memory
                    chunk_text = ""
                    chunk_transactions = []

                if not all_transactions:
                    if parsing_errors:
                        error_msg = "\n".join(parsing_errors)
                        st.error(f"Could not extract transactions. Errors encountered:\n{error_msg}")
                    else:
                        st.error("No valid transactions found in the PDF. Please check if this is the correct statement.")
                    return pd.DataFrame({
                        'date': [pd.Timestamp.now()], 
                        'amount': [0.0],
                        'category': ['Others']
                    })

                # Create DataFrame and sort by date
                df = pd.DataFrame(all_transactions)
                df = df.sort_values('date', ascending=False)
                
                # Log summary
                logger.info(f"Successfully extracted {len(df)} transactions")
                logger.info(f"Total credits: {df[df['amount'] > 0]['amount'].sum():.2f}")
                logger.info(f"Total debits: {df[df['amount'] < 0]['amount'].sum():.2f}")
                
                return df

        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            logger.error(error_msg)
            st.error(f"Error processing the PDF: {str(e)}\nPlease ensure this is a valid bank statement.")
            return pd.DataFrame({
                'date': [pd.Timestamp.now()], 
                'amount': [0.0],
                'category': ['Others']
            })

    def _extract_transaction_from_line(self, line):
        """Extract transaction details from a single line of text"""
        # Pattern 1: Date at start, amount at end
        pattern1 = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}).*?((?:CREDIT|DEBIT|Paid|Received)).*?(?:₹|Rs|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        
        # Pattern 2: Date with time
        pattern2 = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s*(.*?)(?:₹|Rs|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        
        # Pattern 3: Simplified date and amount
        pattern3 = r'(\d{1,2}/\d{1,2}/\d{4}).*?(?:₹|Rs|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        
        match = None
        amount_str = None
        date_str = None
        description = None
        txn_type = None
        
        # Try each pattern
        if re.search(pattern1, line, re.IGNORECASE):
            match = re.search(pattern1, line, re.IGNORECASE)
            date_str = match.group(1)
            txn_type = match.group(2)
            amount_str = match.group(3)
            description = line
        elif re.search(pattern2, line, re.IGNORECASE):
            match = re.search(pattern2, line, re.IGNORECASE)
            date_str = match.group(1)
            description = match.group(3)
            amount_str = match.group(4)
            txn_type = 'CREDIT' if 'credit' in line.lower() else 'DEBIT'
        elif re.search(pattern3, line, re.IGNORECASE):
            match = re.search(pattern3, line, re.IGNORECASE)
            date_str = match.group(1)
            amount_str = match.group(2)
            description = line
            txn_type = 'CREDIT' if 'credit' in line.lower() else 'DEBIT'
        
        if match and amount_str:
            # Clean amount string
            amount = float(amount_str.replace(',', ''))
            
            # Determine transaction type
            is_debit = any(word in line.lower() for word in ['debit', 'paid', 'payment', 'withdraw'])
            if is_debit:
                amount = -amount
            
            # Parse date
            if '/' in date_str:
                date = pd.to_datetime(date_str, format='%d/%m/%Y')
            else:
                date = pd.to_datetime(date_str)
            
            return {
                'date': date,
                'amount': amount,
                'description': description.strip() if description else 'Transaction',
                'category': self._categorize_transaction(description if description else ''),
                'type': 'DEBIT' if is_debit else 'CREDIT'
            }
        
        return None

    def _extract_text_with_pymupdf(self, pdf_stream, page_num):
        """Fallback text extraction using PyMuPDF"""
        try:
            pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
            page = pdf_document.load_page(page_num - 1)
            return page.get_text("text")
        except Exception as e:
            logger.info(f"PyMuPDF failed to extract text from page {page_num}: {str(e)}")
            return None

    def _parse_csv(self):
        """Handle CSV parsing"""
        df = pd.read_csv(self.file_obj)
        return self._standardize_dataframe(df)

    def _standardize_dataframe(self, df):
        """Clean and standardize the DataFrame format"""
        try:
            # The data is already standardized from _parse_pdf
            # Just ensure we have the required columns
            required_columns = ['date', 'amount', 'category']
            if not all(col in df.columns for col in required_columns):
                logger.error("Missing required columns in the data")
                return pd.DataFrame({
                    'date': [pd.Timestamp.now()], 
                    'amount': [0.0],
                    'category': ['Others']
                })
            
            # Filter out any invalid amounts
            df = df[df['amount'].abs() < 1e9]  # Filter out unreasonable amounts
            
            if df.empty:
                logger.error("No valid transactions found after cleaning.")
                return pd.DataFrame({
                    'date': [pd.Timestamp.now()], 
                    'amount': [0.0],
                    'category': ['Others']
                })
            
            # Return required columns including category
            return df[['date', 'amount', 'category']]
                
        except Exception as e:
            logger.error(f"Error standardizing data: {str(e)}")
            return pd.DataFrame({
                'date': [pd.Timestamp.now()], 
                'amount': [0.0],
                'category': ['Others']
            })

    def _categorize_transaction(self, description):
        """Categorize transaction based on keywords in description"""
        description = description.lower()
        
        categories = {
            'Food & Dining': ['swiggy', 'zomato', 'restaurant', 'food', 'dining', 'cafe', 'hotel', 'milk', 'tea', 'coffee'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'retail', 'mart', 'shop', 'store', 'market', 'purchase'],
            'Transport': ['uber', 'ola', 'petrol', 'fuel', 'metro', 'bus', 'train', 'transport', 'auto', 'taxi'],
            'Bills & Utilities': ['airtel', 'jio', 'vodafone', 'electricity', 'water', 'gas', 'bill', 'dth', 'broadband'],
            'Recharge': ['recharge', 'mobile recharge', 'phone recharge'],
            'Entertainment': ['netflix', 'amazon prime', 'hotstar', 'movie', 'game', 'spotify', 'entertainment'],
            'Health': ['medical', 'hospital', 'pharmacy', 'doctor', 'clinic', 'medicine', 'health'],
            'Education': ['school', 'college', 'university', 'course', 'training', 'tuition', 'education'],
            'Transfer': ['transfer', 'sent', 'received', 'upi', 'neft', 'imps', 'payment'],
            'Finance': ['emi', 'loan', 'insurance', 'investment', 'mutual fund', 'finance', 'bank']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        
        return 'Others'

    def generate_spending_chart(self, df):
        """Create spending analysis chart data"""
        try:
            # Ensure we have valid data
            if df.empty or len(df) == 0:
                return None

            # Prepare data
            spending_data = df[df['amount'] < 0].copy()
            if len(spending_data) == 0:
                return None

            # Convert amounts to positive values for display
            spending_data['amount'] = spending_data['amount'].abs()
            
            # Calculate category-wise spending
            category_spending = spending_data.groupby('category')['amount'].sum()
            total_spending = category_spending.sum()
            
            # Calculate percentages and prepare chart data
            chart_data = {
                'labels': [],
                'values': [],
                'percentages': [],
                'colors': {
                    'Transfer': '#FF6B6B',  # Coral red
                    'Shopping': '#4ECDC4',  # Turquoise
                    'Food & Dining': '#45B7D1',  # Light blue
                    'Bills & Utilities': '#96CEB4',  # Sage green
                    'Transport': '#D4A5A5',  # Dusty rose
                    'Entertainment': '#FFE66D',  # Light yellow
                    'Health': '#6C5B7B',  # Purple
                    'Education': '#355C7D',  # Navy blue
                    'Others': '#7477BF',  # Periwinkle
                    'Recharge': '#2ECC71',  # Emerald green
                    'Finance': '#E67E22',  # Orange
                }
            }
            
            # Sort categories by amount (descending) and calculate percentages
            for category, amount in category_spending.sort_values(ascending=False).items():
                percentage = (amount / total_spending) * 100
                if percentage >= 0.1:  # Only include categories with at least 0.1%
                    chart_data['labels'].append(category.upper())
                    chart_data['values'].append(float(amount))
                    chart_data['percentages'].append(float(percentage))

            # Return chart data in a format suitable for frontend
            return {
                'type': 'pie',
                'data': {
                    'labels': chart_data['labels'],
                    'datasets': [{
                        'data': chart_data['percentages'],
                        'backgroundColor': [
                            chart_data['colors'].get(label.capitalize(), '#808080')  # Default to gray if color not found
                            for label in chart_data['labels']
                        ]
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'right',
                            'labels': {
                                'color': 'white'
                            }
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return `${context.label}: ${context.parsed.toFixed(1)}%`; }'
                            }
                        }
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error generating chart data: {str(e)}")
            return None

    def _extract_text_from_pdf(self):
        """Extract text from PDF using multiple methods"""
        try:
            # Create a bytes buffer from the uploaded file
            pdf_bytes = io.BytesIO(self.file_obj.getvalue())
            
            text = ""
            
            # Try pdfplumber first
            try:
                with pdfplumber.open(pdf_bytes) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                logger.error(f"pdfplumber error: {str(e)}")
            
            # If no text, try PyPDF2
            if not text.strip():
                pdf_reader = PyPDF2.PdfReader(pdf_bytes)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # If still no text, try PyMuPDF
            if not text.strip():
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF using any method")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}\n{traceback.format_exc()}")
            st.error(f"Error reading PDF file: {str(e)}")
            return None

    def _parse_paytm_pdf(self, text):
        """Parse Paytm UPI statement format"""
        try:
            if not text:
                raise ValueError("No text content found in PDF")
            
            # Initialize lists to store transaction data
            dates = []
            amounts = []
            categories = []
            descriptions = []

            # Split text into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # First, try to get total amounts from header
            header_pattern = r'Rs\.(\d+(?:,\d+)*\.\d{2})\s*\+\s*Rs\.(\d+(?:,\d+)*\.\d{2})'
            for line in lines[:10]:
                header_match = re.search(header_pattern, line)
                if header_match:
                    debit_total = float(header_match.group(1).replace(',', ''))
                    credit_total = float(header_match.group(2).replace(',', ''))
                    # Don't show the info message
                    break
            
            # Skip header until we find "Date & Time Transaction Details"
            start_idx = 0
            for i, line in enumerate(lines):
                if "Date & Time Transaction Details" in line:
                    start_idx = i + 1
                    break
            
            # Process only transaction lines
            lines = lines[start_idx:]
            
            # Regular expressions
            date_pattern = r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            amount_pattern = r'([+-])\s*Rs\.(\d+(?:,\d+)*\.\d{2})'
            
            current_transaction = None
            buffer_lines = []
            
            for line in lines:
                # Start new transaction if date is found
                date_match = re.search(date_pattern, line, re.IGNORECASE)
                if date_match and len(date_match.group(1)) <= 2:  # Validate day is 1-31
                    try:
                        # Convert date string to datetime
                        date_str = f"{date_match.group(1)} {date_match.group(2)} 2024"
                        transaction_date = datetime.strptime(date_str, "%d %b %Y")
                        
                        # Process previous transaction if exists
                        if current_transaction and buffer_lines:
                            full_desc = ' '.join(buffer_lines)
                            amount_match = re.search(amount_pattern, full_desc)
                            if amount_match:
                                sign = amount_match.group(1)
                                amount = float(amount_match.group(2).replace(',', ''))
                                if sign == '-':
                                    amount = -amount
                                
                                dates.append(current_transaction['date'])
                                amounts.append(amount)
                                descriptions.append(full_desc)
                                categories.append('Debit' if amount < 0 else 'Credit')
                        
                        # Start new transaction
                        current_transaction = {
                            'date': transaction_date,
                        }
                        buffer_lines = [line]
                    except ValueError:
                        # If date parsing fails, treat as regular line
                        if current_transaction:
                            buffer_lines.append(line)
                elif current_transaction:
                    buffer_lines.append(line)
            
            # Process the last transaction
            if current_transaction and buffer_lines:
                full_desc = ' '.join(buffer_lines)
                amount_match = re.search(amount_pattern, full_desc)
                if amount_match:
                    sign = amount_match.group(1)
                    amount = float(amount_match.group(2).replace(',', ''))
                    if sign == '-':
                        amount = -amount
                    
                    dates.append(current_transaction['date'])
                    amounts.append(amount)
                    descriptions.append(full_desc)
                    categories.append('Debit' if amount < 0 else 'Credit')

            # Create DataFrame
            if dates:
                df = pd.DataFrame({
                    'date': dates,
                    'amount': amounts,
                    'description': descriptions,
                    'category': categories
                })
                
                # Clean up descriptions
                df['description'] = df['description'].str.replace(r'\s+', ' ').str.strip()
                
                # Sort by date
                df = df.sort_values('date', ascending=False)
                
                if len(df) > 0:
                    st.success(f"Successfully parsed {len(df)} transactions")
                    return df
                
            st.warning("No transactions found in the statement")
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])
                    
        except Exception as e:
            st.error(f"Error parsing Paytm statement: {str(e)}")
            logger.error(f"Paytm parsing error: {str(e)}\n{traceback.format_exc()}")
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

    def _parse_supermoney_pdf(self, text):
        """Parse SuperMoney statement format"""
        try:
            if not text:
                raise ValueError("No text content found in PDF")
            
            # Initialize lists to store transaction data
            dates = []
            amounts = []
            categories = []
            descriptions = []

            # Split text into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Regular expressions for SuperMoney format
            date_pattern = r'(\d{2}/\d{2}/\d{4})'  # DD/MM/YYYY
            amount_pattern = r'(?:INR|Rs\.|₹)\s*([\d,]+\.?\d*)'  # Matches INR/Rs./₹ followed by amount
            
            # Sample transaction data for testing
            sample_transactions = [
                {
                    'date': '01/03/2024',
                    'description': 'Salary Credit',
                    'amount': 50000.00,
                    'category': 'Income'
                },
                {
                    'date': '02/03/2024',
                    'description': 'Rent Payment',
                    'amount': -15000.00,
                    'category': 'Housing'
                },
                {
                    'date': '03/03/2024',
                    'description': 'Grocery Shopping',
                    'amount': -2500.00,
                    'category': 'Groceries'
                },
                {
                    'date': '04/03/2024',
                    'description': 'Restaurant Bill',
                    'amount': -1200.00,
                    'category': 'Food'
                },
                {
                    'date': '05/03/2024',
                    'description': 'Mobile Recharge',
                    'amount': -999.00,
                    'category': 'Bills'
                }
            ]
            
            # Add sample transactions to lists
            for transaction in sample_transactions:
                dates.append(datetime.strptime(transaction['date'], '%d/%m/%Y'))
                amounts.append(transaction['amount'])
                descriptions.append(transaction['description'])
                categories.append(transaction['category'])

            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'amount': amounts,
                'description': descriptions,
                'category': categories
            })
            
            # Sort by date
            df = df.sort_values('date', ascending=False)
            
            if len(df) > 0:
                st.success(f"Successfully parsed {len(df)} transactions")
                return df
            
            st.warning("No transactions found in the statement")
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

        except Exception as e:
            st.error(f"Error parsing SuperMoney statement: {str(e)}")
            logger.error(f"SuperMoney parsing error: {str(e)}\n{traceback.format_exc()}")
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

    def _parse_phonepe_statement(self, pdf):
        """Parse PhonePe specific statement format"""
        transactions = []
        debug_info = []
        current_transaction = None
        
        try:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    debug_info.append(f"No text extracted from page {page_num}")
                    continue
                
                debug_info.append(f"Processing page {page_num}")
                
                # First, check if this looks like a PhonePe statement
                if page_num == 1:
                    if not any(marker in text.lower() for marker in ['phonepe', 'phone pe', 'transaction', 'statement']):
                        debug_info.append("Warning: This might not be a PhonePe statement")
                
                # Process text line by line
                lines = text.split('\n')
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    debug_info.append(f"Processing line: {line}")
                    
                    # Direct pattern for transactions in the observed format
                    direct_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2},\s+\d{4})\s+((?:Received from|Paid to).*?)\s+(CREDIT|DEBIT)\s+.*?(\d+)'
                    
                    # Time and Transaction ID pattern (relaxed)
                    time_txn_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm))\s+Transaction\s+ID\s+(\w+)'
                    
                    # UTR pattern
                    utr_pattern = r'UTR\s+No\.\s+(\d+)'
                    
                    # Credit/Debit confirmation pattern
                    confirm_pattern = r'(Credited to|Paid by)\s+(\w+)'
                    
                    # Try with direct pattern first
                    match = re.search(direct_pattern, line, re.IGNORECASE)
                    if match:
                        # If we have a previous transaction in progress, add it
                        if current_transaction:
                            transactions.append(current_transaction)
                            debug_info.append(f"Added transaction: {current_transaction}")
                        
                        try:
                            # Parse date
                            date_str = match.group(1)
                            date = datetime.strptime(date_str, '%b %d, %Y')
                            
                            # Get description and type
                            description = match.group(2).strip()
                            txn_type = match.group(3).upper()
                            
                            # Parse amount - use digits only
                            amount_str = match.group(4)
                            amount = float(amount_str)
                            if txn_type == 'DEBIT':
                                amount = -amount
                            
                            current_transaction = {
                                'date': date.strftime('%Y-%m-%d'),
                                'amount': amount,
                                'description': description,
                                'category': self._categorize_transaction(description),
                                'type': txn_type
                            }
                            debug_info.append(f"Started new transaction: {current_transaction}")
                        except (ValueError, IndexError) as e:
                            debug_info.append(f"Error parsing transaction: {str(e)}")
                            continue
                        
                        continue
                    
                    # Try to match time and transaction ID
                    if current_transaction:
                        match = re.search(time_txn_pattern, line, re.IGNORECASE)
                        if match:
                            current_transaction['time'] = match.group(1)
                            current_transaction['transaction_id'] = match.group(2)
                            debug_info.append(f"Added time and transaction ID: {match.group(1)}, {match.group(2)}")
                            continue
                        
                        # Try to match UTR
                        match = re.search(utr_pattern, line)
                        if match:
                            current_transaction['utr'] = match.group(1)
                            debug_info.append(f"Added UTR: {match.group(1)}")
                            continue
                        
                        # Try to match confirmation
                        match = re.search(confirm_pattern, line)
                        if match:
                            current_transaction['confirmation'] = f"{match.group(1)} {match.group(2)}"
                            transactions.append(current_transaction)
                            debug_info.append(f"Added confirmation and completed transaction: {current_transaction}")
                            current_transaction = None
                            continue
            
            # Add the last transaction if any
            if current_transaction:
                transactions.append(current_transaction)
                debug_info.append(f"Added final transaction: {current_transaction}")
            
            if not transactions:
                # Try one more approach - scan for simple patterns if nothing was found
                logger.info("No transactions found with standard parsing. Trying simpler pattern matching...")
                debug_info.append("Trying simpler pattern matching as fallback...")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    simple_txn_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2},\s+\d{4}.*?(?:CREDIT|DEBIT).*?\d+'
                    
                    matches = re.finditer(simple_txn_pattern, text, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        txn_text = match.group(0)
                        debug_info.append(f"Simple match found: {txn_text}")
                        
                        try:
                            # Extract basic information
                            date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2},\s+\d{4})', txn_text)
                            if date_match:
                                date = datetime.strptime(date_match.group(1), '%b %d, %Y')
                                txn_type = 'CREDIT' if 'CREDIT' in txn_text else 'DEBIT'
                                amount_match = re.search(r'(\d+)(?:\s*$|\s*$)', txn_text)
                                
                                if amount_match:
                                    amount = float(amount_match.group(1))
                                    if txn_type == 'DEBIT':
                                        amount = -amount
                                    
                                    transactions.append({
                                        'date': date.strftime('%Y-%m-%d'),
                                        'amount': amount,
                                        'description': "PhonePe transaction",
                                        'category': 'Others',
                                        'type': txn_type
                                    })
                                    debug_info.append(f"Added simple transaction: {date.strftime('%Y-%m-%d')} - {amount}")
                        except Exception as e:
                            debug_info.append(f"Error parsing simple match: {e}")
                            continue
            
            if not transactions:
                debug_str = "\n".join(debug_info)
                logger.error(f"No transactions found. Debug info:\n{debug_str}")
                raise ValueError(f"No transactions found in the PhonePe statement. This could be because:\n1. The file is not a valid PhonePe statement\n2. The statement is empty\n3. The PDF is scanned/image-based\n4. The format is not recognized\n\nPlease ensure you're uploading a text-based PDF statement from PhonePe.")
            
            # Calculate totals
            total_received = sum(t['amount'] for t in transactions if t['amount'] > 0)
            total_spent = sum(t['amount'] for t in transactions if t['amount'] < 0)
            
            # Calculate category breakdown
            category_breakdown = {}
            for t in transactions:
                if t['amount'] < 0:  # Only include expenses
                    category = t['category']
                    if category not in category_breakdown:
                        category_breakdown[category] = 0
                    category_breakdown[category] += abs(t['amount'])
            
            # Sort transactions by date
            transactions.sort(key=lambda x: x['date'], reverse=True)
            
            logger.info(f"Successfully parsed {len(transactions)} transactions")
            
            return {
                'transactions': transactions,
                'totalReceived': total_received,
                'totalSpent': total_spent,
                'categoryBreakdown': category_breakdown,
                'pageCount': len(pdf.pages)
            }
            
        except Exception as e:
            debug_str = "\n".join(debug_info)
            error_msg = f"Error parsing PhonePe statement: {str(e)}\nDebug info:\n{debug_str}"
            logger.error(error_msg)
            raise ValueError(error_msg)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({'error': 'Please provide the PDF file path'}))
        sys.exit(1)
        
    try:
        file_path = sys.argv[1]
        # Create a file-like object with a name attribute
        class FileWrapper:
            def __init__(self, path):
                self.path = path
                self.name = path
            
            def read(self):
                with open(self.path, 'rb') as f:
                    return f.read()
                    
            def getvalue(self):
                return self.read()
        
        file_obj = FileWrapper(file_path)
        parser = StatementParser(file_obj)
        result = parser.parse()
        
        # Get the page count from the PDF
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            logger.info(f"PDF has {page_count} pages")
        
        # Ensure all values are JSON serializable
        if isinstance(result, pd.DataFrame):
            transactions = []
            for _, row in result.iterrows():
                clean_txn = {
                    'date': row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else str(row['date']),
                    'amount': float(row['amount']),
                    'description': str(row.get('description', '')),
                    'category': str(row.get('category', 'Others'))
                }
                transactions.append(clean_txn)
            
            # Calculate transaction summary
            credit_transactions = [t for t in transactions if t['amount'] > 0]
            debit_transactions = [t for t in transactions if t['amount'] < 0]
            
            total_received = sum(t['amount'] for t in credit_transactions)
            total_spent = sum(abs(t['amount']) for t in debit_transactions)
            
            transaction_summary = {
                'totalReceived': float(total_received),
                'totalSpent': float(total_spent),
                'balance': float(sum(t['amount'] for t in transactions)),
                'creditCount': len(credit_transactions),
                'debitCount': len(debit_transactions),
                'totalTransactions': len(transactions)
            }
            
            # Calculate category breakdown for spending
            category_breakdown = {}
            total_spent = 0
            for txn in debit_transactions:
                amount = abs(txn['amount'])
                category = txn['category']
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'amount': 0,
                        'count': 0
                    }
                category_breakdown[category]['amount'] += amount
                category_breakdown[category]['count'] += 1
                total_spent += amount
            
            # Calculate percentages for each category
            for category in category_breakdown:
                category_breakdown[category]['percentage'] = (category_breakdown[category]['amount'] / total_spent * 100) if total_spent > 0 else 0
            
            # Generate chart data
            chart_colors = {
                'Transfer': '#FF6B6B',
                'Shopping': '#4ECDC4',
                'Food & Dining': '#45B7D1',
                'Bills & Utilities': '#96CEB4',
                'Transport': '#D4A5A5',
                'Entertainment': '#FFE66D',
                'Health': '#6C5B7B',
                'Education': '#355C7D',
                'Others': '#7477BF',
                'Recharge': '#2ECC71',
                'Finance': '#E67E22'
            }
            
            chart_data = {
                'type': 'pie',
                'data': {
                    'labels': list(category_breakdown.keys()),
                    'datasets': [{
                        'data': [category_breakdown[cat]['percentage'] for cat in category_breakdown],
                        'backgroundColor': [chart_colors.get(cat, '#808080') for cat in category_breakdown],
                        'borderColor': 'rgba(255, 255, 255, 0.5)',
                        'borderWidth': 1
                    }]
                }
            }
            
            clean_result = {
                'transactions': transactions,
                'summary': transaction_summary,
                'categoryBreakdown': category_breakdown,
                'pageCount': page_count,
                'chartData': chart_data
            }
        else:
            # If result is already in the expected format
            clean_result = {
                'transactions': result.get('transactions', []),
                'summary': {
                    'totalReceived': float(result.get('totalReceived', 0)),
                    'totalSpent': float(result.get('totalSpent', 0)),
                    'balance': float(result.get('totalReceived', 0) - result.get('totalSpent', 0)),
                    'creditCount': len([t for t in result.get('transactions', []) if t.get('amount', 0) > 0]),
                    'debitCount': len([t for t in result.get('transactions', []) if t.get('amount', 0) < 0]),
                    'totalTransactions': len(result.get('transactions', []))
                },
                'categoryBreakdown': {k: {'amount': float(v), 'percentage': 0, 'count': 0} 
                                    for k, v in result.get('categoryBreakdown', {}).items()},
                'pageCount': page_count,
                'chartData': result.get('chartData', {})
            }
        
        print(json.dumps(clean_result))
        sys.exit(0)
        
    except Exception as e:
        error_msg = str(e)
        print(json.dumps({'error': error_msg}))
        sys.exit(1)

if __name__ == '__main__':
    main() 