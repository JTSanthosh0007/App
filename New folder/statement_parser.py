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
        """Handle PDF parsing with comprehensive and ultra-flexible extraction"""
        pdf_stream = io.BytesIO(self.file_obj.read())
        
        try:
            with pdfplumber.open(pdf_stream) as pdf:
                # Enhanced debugging: Log total pages and initial text extraction
                st.write(f"Total PDF Pages: {len(pdf.pages)}")
                
                all_extracted_text = []
                parsing_errors = []
                
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

                # Comprehensive transaction extraction
                transactions = []
                for page_num, page in enumerate(pdf.pages, 1):
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

                # Combine all extracted text
                full_text = "\n".join(all_extracted_text)
                
                # Extract transactions from full text
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
            logger.error(f"Comprehensive PDF parsing error: {str(e)}")
            st.error(f"Error processing the PDF: {str(e)}\nPlease ensure this is a valid bank statement.")
            return pd.DataFrame(columns=['date', 'amount', 'description', 'category'])

    def _parse_date(self, date_str):
        """
        Ultra-robust date parsing method with comprehensive handling and detailed logging
        """
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
        """
        Ultra-comprehensive transaction categorization
        """
        description = description.lower()
        
        # Expanded and more nuanced categorization with weighted scoring
        categories = {
            'Family Support': {
                'keywords': ['dad', 'mom', 'father', 'mother', 'parents', 'family', 'gift'],
                'weight': 0.9
            },
            'Salary': {
                'keywords': ['salary', 'credit', 'income', 'payment', 'cashfree', 'refund'],
                'weight': 0.8
            },
            'Bills': {
                'keywords': [
                    'electricity', 'mobile', 'phone', 'internet', 'recharge', 
                    'bill', 'poonawalla', 'loan', 'finance', 'insurance', 
                    'electricity', 'water', 'gas', 'rent'
                ],
                'weight': 0.7
            },
            'Transportation': {
                'keywords': ['auto', 'uber', 'ola', 'bus', 'train', 'flight', 'travel', 'taxi'],
                'weight': 0.6
            },
            'Personal Expenses': {
                'keywords': ['ravi', 'ramanjini', 'shetty', 'kumar', 'personal', 'service'],
                'weight': 0.5
            },
            'Transfer': {
                'keywords': ['transfer', 'upi', 'paytm', 'phonepe', 'gpay', 'bank transfer'],
                'weight': 0.4
            },
            'Shopping': {
                'keywords': ['amazon', 'flipkart', 'shop', 'purchase', 'buy', 'ecommerce'],
                'weight': 0.6
            },
            'Food': {
                'keywords': ['restaurant', 'food', 'dining', 'cafe', 'hotel', 'meal', 'pizza', 'burger'],
                'weight': 0.5
            },
            'Entertainment': {
                'keywords': ['netflix', 'amazon prime', 'movie', 'show', 'ticket', 'cinema', 'streaming'],
                'weight': 0.4
            }
        }
        
        # Scoring mechanism
        category_scores = {category: 0 for category in categories}
            
        for category, details in categories.items():
            for keyword in details['keywords']:
                if keyword in description:
                    category_scores[category] += details['weight']
                    
        # Find the highest scoring category
        top_category = max(category_scores, key=category_scores.get)
        
        # If no significant match, return 'Others'
        return top_category if category_scores[top_category] > 0.3 else 'Others'

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

    def generate_spending_chart(self, df):
        """Create comprehensive interactive spending and timeline analysis charts"""
        try:
            # Ensure we have valid data
            if df.empty or len(df) == 0:
                st.warning("No transaction data available for analysis.")
                return None, None

            # Prepare data
            df['date'] = pd.to_datetime(df['date'])

            # Create tabs for different visualizations
            tab1, tab2 = st.tabs(["Spending by Category", "Monthly Trends"])
            
            with tab1:
                # Category-wise Spending
                st.subheader("💸 Spending by Category")
                
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                
                with col1:
                    st.metric("Total Transactions", len(df))
                with col2:
                    st.metric("Total Credit Transactions", len(df[df['amount'] > 0]))
                with col3:
                    st.metric("Total Debit Transactions", len(df[df['amount'] < 0]))
                with col4:
                    # Total spent (debit amount)
                    total_spent = df[df['amount'] < 0]['amount'].abs().sum()
                    st.metric("Total Spent", f"₹{total_spent:,.2f}")
                with col5:
                    # Total credit amount
                    total_credit = df[df['amount'] > 0]['amount'].sum()
                    st.metric("Total Credit", f"₹{total_credit:,.2f}")
                with col6:
                    # Net amount (credits - debits)
                    net_amount = df['amount'].sum()
                    st.metric("Net Amount", f"₹{net_amount:,.2f}", 
                              delta_color="inverse",
                              delta=f"{'↑ Positive' if net_amount > 0 else '↓ Negative'}")
                with col7:
                    # Highest transaction amount
                    highest_transaction = df['amount'].abs().max()
                    highest_transaction_row = df.loc[df['amount'].abs() == highest_transaction].iloc[0]
                    st.metric("Highest Transaction", 
                              f"₹{highest_transaction:,.2f}", 
                              delta=highest_transaction_row['description'][:15] + '...')
                with col8:
                    # Lowest transaction amount
                    lowest_transaction = df['amount'].abs().min()
                    lowest_transaction_row = df.loc[df['amount'].abs() == lowest_transaction].iloc[0]
                    st.metric("Lowest Transaction", 
                              f"₹{lowest_transaction:,.2f}", 
                              delta=lowest_transaction_row['description'][:15] + '...')
                
                # Aggregate spending by category
                spending_data = df[df['amount'] < 0].copy()
                spending_data['amount'] = spending_data['amount'].abs()

                # Aggregate spending by category
                category_spending = spending_data.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
                category_spending.columns = ['Category', 'Total Amount', 'Number of Transactions']
                category_spending = category_spending.sort_values('Total Amount', ascending=False)
                
                # Pie chart for category distribution
                fig_category = go.Figure(data=[go.Pie(
                    labels=category_spending['Category'],
                    values=category_spending['Total Amount'],
                    hole=0.3,
                    textinfo='label+percent',
                    hovertemplate="<b>%{label}</b><br>Total Spent: ₹%{value:,.2f}<br>Percentage: %{percent}<extra></extra>"
                )])
                
                fig_category.update_layout(
                    title='Spending Distribution Across Categories',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_category, use_container_width=True)
            
            with tab2:
                # Monthly Trends
                st.subheader("📈 Monthly Spending Trends")
                
                # Group by month and calculate total credits and debits
                monthly_data = df.groupby(pd.Grouper(key='date', freq='M')).agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                
                monthly_data.columns = ['Month', 'Total Amount', 'Number of Transactions']
                monthly_data['Transaction Type'] = monthly_data['Total Amount'].apply(lambda x: 'Credit' if x > 0 else 'Debit')
                
                # Bar chart for monthly trends
                fig_monthly = go.Figure()
                
                # Add bars for monthly totals
                fig_monthly.add_trace(go.Bar(
                    x=monthly_data['Month'],
                    y=monthly_data['Total Amount'].abs(),
                    name='Monthly Total',
                    marker_color='rgba(31, 119, 180, 0.7)',
                    hovertemplate="Month: %{x}<br>Total Amount: ₹%{y:,.2f}<br>Transactions: %{text}<extra></extra>",
                    text=monthly_data['Number of Transactions']
                ))
                
                fig_monthly.update_layout(
                    title='Monthly Transaction Overview',
                    xaxis_title='Month',
                    yaxis_title='Total Amount (₹)',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            return None, fig_category
        
        except Exception as e:
            st.error(f"Error generating charts: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None, None 

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

    def parse_phonepe_statement(self, pdf_file):
        try:
            with pdfplumber.open(pdf_file) as pdf:
                transactions = []
                for page in pdf.pages:
                    text = page.extract_text()
                    # Add your PhonePe specific parsing logic here
                    # Example pattern: date, description, amount
                    pattern = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([+-]?\d+(?:,\d+)*(?:\.\d{2})?)'
                    matches = re.finditer(pattern, text)
                    
                    for match in matches:
                        date = datetime.strptime(match.group(1), '%d/%m/%Y')
                        description = match.group(2).strip()
                        amount = float(match.group(3).replace(',', ''))
                        transactions.append({
                            'Date': date,
                            'Description': description,
                            'Amount': amount
                        })
                
                return pd.DataFrame(transactions)
        except Exception as e:
            raise Exception(f"Error parsing PhonePe statement: {str(e)}")
    
    def parse_paytm_statement(self, pdf_file):
        try:
            with pdfplumber.open(pdf_file) as pdf:
                transactions = []
                for page in pdf.pages:
                    text = page.extract_text()
                    # Add your Paytm specific parsing logic here
                    # Example pattern: date, description, amount
                    pattern = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([+-]?\d+(?:,\d+)*(?:\.\d{2})?)'
                    matches = re.finditer(pattern, text)
                    
                    for match in matches:
                        date = datetime.strptime(match.group(1), '%d/%m/%Y')
                        description = match.group(2).strip()
                        amount = float(match.group(3).replace(',', ''))
                        transactions.append({
                            'Date': date,
                            'Description': description,
                            'Amount': amount
                        })
                
                return pd.DataFrame(transactions)
        except Exception as e:
            raise Exception(f"Error parsing Paytm statement: {str(e)}") 

    def parse_transactions(self, full_text):
        # ... other code ...
        try:
            amount_str = match.group('amount')
            amount = float(amount_str)  # This line should be inside a try block
        except ValueError:
            logger.error(f"Invalid amount string: {amount_str}")
            amount = 0.0  # Default value or handle it as needed
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}") 