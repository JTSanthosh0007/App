import pandas as pd
import plotly.express as px
import pdfplumber
from pathlib import Path
import io
import streamlit as st
import re
from pdfminer.layout import LAParams
import PyPDF2
import fitz  # PyMuPDF
import traceback  # Import traceback for detailed error logging
import logging  # Import logging for error handling
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
import argparse
from functools import lru_cache
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatementParser:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.transactions = []
        self._category_cache = {}

    @st.cache_data(ttl=3600)  # Cache for 1 hour
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
            # Use PyMuPDF for faster PDF parsing
            doc = fitz.open(stream=self.file_obj.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            
            if 'kotak' in self.file_obj.name.lower() or 'kotak' in text.lower():
                return self._parse_kotak_pdf(text)
            
            # Process text in parallel using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Split text into chunks for parallel processing
                chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
                results = list(executor.map(self._process_text_chunk, chunks))
            
            # Combine results
            transactions = []
            for result in results:
                transactions.extend(result)
            
            return transactions
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _parse_date(self, date_str):
        try:
            # ... existing code ...
            pass
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @lru_cache(maxsize=1000)
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
            'Food & Dining': {
                'keywords': [
        'restaurant', 'food', 'dining', 'cafe', 'hotel', 'meal', 'fast food', 'street food',
        'buffet', 'takeaway', 'home delivery', 'drive-thru', 'fine dining', 'food truck',
        'catering', 'brunch', 'lunch', 'dinner', 'breakfast', 'snacks', 'midnight snack',
        'mcdonalds', 'kfc', 'dominos', 'pizza hut', 'burger king', 'subway', 'starbucks',
        'dunkin donuts', 'hard rock cafe', 'taco bell', 'chipotle', 'wendys', 'panda express',
                    'krispy kreme', 'baskin robbins', 'five guys', 'carls jr', 'popeyes', "arby's", 'in-n-out',
        'zomato', 'swiggy', 'ubereats', 'foodpanda', 'dunzo', 'grubhub', 'doordash', 
        'postmates', 'deliveroo', 'just eat',
                    'grocery', 'supermarket', 'market', 'store', 'shop', 'bazaar', 'mart',
                    'vegetables', 'fruits', 'meat', 'fish', 'dairy', 'bakery', 'deli',
                    'spices', 'herbs', 'condiments', 'beverages', 'snacks', 'candy', 'chocolate',
                    'organic', 'fresh', 'frozen', 'canned', 'packaged', 'bulk'
                ],
                'weight': 0.8
            },
            'Transportation': {
                'keywords': [
                    'uber', 'ola', 'lyft', 'taxi', 'cab', 'auto', 'rickshaw', 'bus', 'train', 'metro',
                    'subway', 'tram', 'ferry', 'flight', 'airline', 'airport', 'railway', 'station',
                    'petrol', 'diesel', 'gas', 'fuel', 'oil', 'lubricant', 'maintenance', 'service',
                    'repair', 'tire', 'battery', 'spare parts', 'car wash', 'parking', 'toll',
                    'insurance', 'registration', 'license', 'permit', 'tax', 'fine', 'penalty',
                    'bicycle', 'scooter', 'motorcycle', 'bike', 'cycle', 'walking', 'jogging',
                    'running', 'exercise', 'fitness', 'gym', 'sports', 'recreation'
                ],
                'weight': 0.85
            },
            'Shopping & Retail': {
                'keywords': [
                    'amazon', 'flipkart', 'myntra', 'ajio', 'nykaa', 'purplle', 'firstcry',
                    'shopclues', 'snapdeal', 'paytm mall', 'jiomart', 'bigbasket', 'grofers',
                    'dunzo', 'zepto', 'blinkit', 'swiggy instamart', 'bigbazaar', 'dmart',
                    'reliance fresh', 'spencer', 'more', 'easyday', 'nature\'s basket',
                    'clothing', 'apparel', 'fashion', 'accessories', 'jewelry', 'watches',
                    'footwear', 'bags', 'wallets', 'cosmetics', 'beauty', 'personal care',
                    'electronics', 'gadgets', 'mobiles', 'laptops', 'computers', 'tablets',
                    'home', 'furniture', 'decor', 'kitchen', 'bath', 'bedding', 'linens',
                    'toys', 'games', 'books', 'stationery', 'sports', 'fitness', 'outdoor',
                    'garden', 'pets', 'automotive', 'tools', 'hardware', 'construction'
                ],
                'weight': 0.75
            },
            'Entertainment & Leisure': {
                'keywords': [
                    'netflix', 'amazon prime', 'hotstar', 'sony liv', 'zee5', 'voot', 'altbalaji',
                    'mx player', 'youtube premium', 'spotify', 'apple music', 'gaana', 'wynk',
                    'jiosaavn', 'hungama', 'bookmyshow', 'inox', 'pvr', 'cinepolis', 'imax',
                    'theatre', 'cinema', 'movie', 'concert', 'show', 'performance', 'event',
                    'ticket', 'booking', 'reservation', 'amusement park', 'theme park', 'water park',
                    'zoo', 'aquarium', 'museum', 'gallery', 'exhibition', 'fair', 'carnival',
                    'festival', 'party', 'celebration', 'gathering', 'meeting', 'conference',
                    'seminar', 'workshop', 'training', 'course', 'class', 'lesson', 'tutorial'
                ],
                'weight': 0.7
            },
            'Health & Medical': {
                'keywords': [
                    'hospital', 'clinic', 'doctor', 'physician', 'specialist', 'surgeon',
                    'dentist', 'orthodontist', 'ophthalmologist', 'optometrist', 'pharmacy',
                    'medical store', 'chemist', 'drugstore', 'medicine', 'prescription',
                    'vaccination', 'immunization', 'checkup', 'examination', 'diagnosis',
                    'treatment', 'therapy', 'surgery', 'operation', 'procedure', 'test',
                    'laboratory', 'pathology', 'radiology', 'x-ray', 'scan', 'ultrasound',
                    'mri', 'ct scan', 'ecg', 'blood test', 'urine test', 'stool test',
                    'insurance', 'claim', 'coverage', 'premium', 'deductible', 'copay',
                    'ambulance', 'emergency', 'urgent care', 'first aid', 'bandage',
                    'ointment', 'cream', 'tablet', 'capsule', 'syrup', 'injection'
                ],
                'weight': 0.9
            },
            'Education & Learning': {
                'keywords': [
                    'school', 'college', 'university', 'institute', 'academy', 'training',
                    'course', 'class', 'lecture', 'seminar', 'workshop', 'tutorial',
                    'tuition', 'coaching', 'mentoring', 'guidance', 'counseling',
                    'book', 'textbook', 'reference', 'study material', 'stationery',
                    'pen', 'pencil', 'notebook', 'paper', 'folder', 'bag', 'uniform',
                    'fee', 'tuition fee', 'admission fee', 'examination fee',
                    'library', 'laboratory', 'computer lab', 'sports facility',
                    'scholarship', 'grant', 'loan', 'financial aid', 'bursary',
                    'certificate', 'diploma', 'degree', 'qualification', 'skill',
                    'knowledge', 'learning', 'education', 'training', 'development'
                ],
                'weight': 0.85
            },
            'Utilities & Bills': {
                'keywords': [
                    'electricity', 'power', 'energy', 'water', 'gas', 'fuel', 'petrol',
                    'diesel', 'lpg', 'cng', 'telephone', 'mobile', 'internet', 'broadband',
                    'cable', 'satellite', 'tv', 'television', 'radio', 'newspaper', 'magazine',
                    'subscription', 'membership', 'rent', 'lease', 'mortgage', 'loan',
                    'insurance', 'tax', 'duty', 'fee', 'charge', 'bill', 'payment',
                    'maintenance', 'service', 'repair', 'upkeep', 'cleaning', 'sanitation',
                    'waste', 'garbage', 'sewage', 'drainage', 'security', 'safety',
                    'emergency', 'fire', 'police', 'ambulance', 'hospital', 'medical'
                ],
                'weight': 0.8
            },
            'Travel & Tourism': {
                'keywords': [
                    'flight', 'airline', 'airport', 'train', 'railway', 'station', 'bus',
                    'coach', 'car', 'taxi', 'cab', 'auto', 'rickshaw', 'bicycle', 'scooter',
                    'motorcycle', 'bike', 'cycle', 'walking', 'jogging', 'running', 'exercise',
                    'hotel', 'resort', 'motel', 'inn', 'lodge', 'guest house', 'hostel',
                    'apartment', 'villa', 'cottage', 'cabin', 'tent', 'camping', 'caravan',
                    'tour', 'package', 'holiday', 'vacation', 'trip', 'journey', 'voyage',
                    'expedition', 'safari', 'cruise', 'yacht', 'boat', 'ship', 'ferry',
                    'ticket', 'booking', 'reservation', 'passport', 'visa', 'permit',
                    'insurance', 'guide', 'map', 'compass', 'camera', 'binoculars'
                ],
                'weight': 0.75
            },
            'Investments & Savings': {
                'keywords': [
                    'bank', 'account', 'savings', 'current', 'fixed deposit', 'recurring deposit',
                    'investment', 'stock', 'share', 'equity', 'mutual fund', 'etf', 'bonds',
                    'debentures', 'nps', 'ppf', 'epf', 'insurance', 'life insurance',
                    'health insurance', 'term insurance', 'ulip', 'endowment', 'pension',
                    'annuity', 'retirement', 'gold', 'silver', 'platinum', 'diamond',
                    'property', 'real estate', 'land', 'house', 'apartment', 'commercial',
                    'rental', 'lease', 'mortgage', 'loan', 'credit', 'debit', 'transaction',
                    'transfer', 'withdrawal', 'deposit', 'interest', 'dividend', 'profit',
                    'loss', 'gain', 'return', 'yield', 'growth', 'appreciation'
                ],
                'weight': 0.9
            },
            'UPI & Wallets': {
                'keywords': [
                    'paytm', 'phonepe', 'google pay', 'gpay', 'bhim', 'amazon pay', 'mobikwik', 'freecharge', 'airtel money', 'jiomoney'
                ],
                'weight': 0.9
            },
            'Indian Banks': {
                'keywords': [
                    'sbi', 'state bank of india', 'hdfc', 'icici', 'axis', 'kotak', 'pnb', 'canara', 'union bank', 'bank of baroda', 'idfc', 'yes bank', 'indusind', 'uco', 'central bank', 'bank of india', 'rbl', 'federal bank', 'karur vysya', 'dcb', 'south indian bank'
                ],
                'weight': 0.9
            },
            'Jewellery': {
                'keywords': [
                    'tanishq', 'kalyan', 'malabar', 'pc jeweller', 'joyallukas', 'tribhovandas', 'senco', 'tbz', 'bhima', 'lalitha', 'gitanjali'
                ],
                'weight': 0.7
            },
            'Mutual Funds & Stocks': {
                'keywords': [
                    'zerodha', 'groww', 'upstox', 'icici direct', 'hdfc securities', 'angel broking', 'motilal oswal', 'sharekhan', '5paisa', 'kotak securities', 'axis direct'
                ],
                'weight': 0.8
            },
            'Government Services': {
                'keywords': [
                    'income tax', 'gst', 'epfo', 'nps', 'uidai', 'passport seva', 'pan card', 'aadhaar', 'voter id', 'driving license', 'parivahan', 'digilocker', 'bharat billpay', 'bharat gas', 'indane', 'hp gas', 'municipal', 'property tax', 'water bill', 'electricity bill', 'mseva', 'seva kendra', 'state government', 'central government', 'railway', 'irctc', 'post office', 'india post', 'court fee', 'stamp duty', 'registration fee', 'e-district', 'e-mitra', 'ap online', 'mp online', 'mahaonline', 'sugam', 'sakala', 'mee seva', 'ts online', 'bhoomi', 'land records', 'ration card', 'pds', 'election commission', 'swachh bharat', 'pm kisan', 'pmay', 'ayushman', 'jan dhan', 'digital india', 'bharat net', 'umang', 'mygov', 'eshram', 'labour', 'pf', 'esi', 'state transport', 'rto', 'municipal corporation', 'gram panchayat', 'zilla parishad', 'block office', 'collectorate', 'tehsil', 'taluka', 'mandal', 'ward', 'urban local body', 'panchayat', 'gram sabha', 'sarpanch', 'mla', 'mp', 'govt', 'gov', 'govt. of india', 'govt of india', 'govt of', 'govt.', 'gov.'
                ],
                'weight': 0.8
            },
            'Gold & Jewellery': {
                'keywords': [
                    'tanishq', 'kalyan', 'malabar', 'pc jeweller', 'joyallukas', 'tribhovandas', 'senco', 'tbz', 'bhima', 'lalitha', 'gitanjali', 'kiran gems', 'shubh jewellers', 'rivaah', 'caratlane', 'bluestone', 'jewellery', 'gold', 'silver', 'diamond', 'platinum', 'bullion', 'ornament', 'bangle', 'ring', 'necklace', 'earring', 'bracelet', 'mangalsutra', 'nosepin', 'chain', 'coin', 'bar', 'jeweler', 'jewellers', 'jewellery shop', 'jewelry', 'jeweler', 'jewellers', 'jewellery store', 'jewelry store'
                ],
                'weight': 0.7
            },
            'Recharge & Bill Payment': {
                'keywords': [
                    'paytm recharge', 'freecharge recharge', 'mobikwik recharge', 'airtel recharge', 'jio recharge', 'vi recharge', 'bsnl recharge', 'tata sky recharge', 'd2h recharge', 'electricity bill', 'water bill', 'gas bill', 'broadband bill', 'mobile bill', 'landline bill', 'postpaid bill', 'prepaid recharge', 'dth recharge', 'tv recharge', 'insurance premium', 'loan emi', 'credit card bill', 'fastag', 'metro card', 'smart card', 'utility bill', 'billdesk', 'bharat billpay', 'npci', 'upi', 'wallet', 'bill payment', 'recharge', 'topup', 'top-up', 'bill', 'payment', 'emi', 'installment', 'subscription', 'renewal'
                ],
                'weight': 0.8
            },
            'Indian Banks': {
                'keywords': [
                    'sbi', 'state bank of india', 'hdfc', 'icici', 'axis', 'kotak', 'pnb', 'canara', 'union bank', 'bank of baroda', 'idfc', 'yes bank', 'indusind', 'uco', 'central bank', 'bank of india', 'rbl', 'federal bank', 'karur vysya', 'dcb', 'south indian bank', 'bandhan', 'idbi', 'city union', 'tamilnad mercantile', 'saraswat', 'syndicate', 'vijaya', 'dena', 'andhra', 'corporation', 'indian overseas', 'punjab & sind', 'karnataka bank', 'dhanlaxmi', 'lakshmi vilas', 'catholic syrian', 'nkgsb', 'apna sahakari', 'saraswat', 'shamrao vithal', 'cosmos', 'janata sahakari', 'bharatiya mahila', 'abhyudaya', 'tjsb', 'suryoday', 'utkarsh', 'au small finance', 'equitas', 'ujjivan', 'esaf', 'fincare', 'nsdl', 'nsdl payments', 'nsdl jiffy', 'fincare', 'fino', 'fino payments', 'paytm payments', 'india post payments', 'jio payments', 'airtel payments', 'aditya birla payments', 'north east small finance', 'capital small finance', 'suryoday small finance', 'utkarsh small finance', 'esaf small finance', 'au small finance', 'equitas small finance', 'ujjivan small finance', 'fincare small finance', 'shivalik small finance', 'jana small finance', 'suryoday small finance', 'utkarsh small finance', 'esaf small finance', 'au small finance', 'equitas small finance', 'ujjivan small finance', 'fincare small finance', 'shivalik small finance', 'jana small finance'
                ],
                'weight': 0.9
            },
            'UPI & Wallets': {
                'keywords': [
                    'paytm', 'phonepe', 'google pay', 'gpay', 'bhim', 'amazon pay', 'mobikwik', 'freecharge', 'airtel money', 'jiomoney', 'payzapp', 'citrus', 'itz cash', 'oxigen', 'ybl', 'nsdl payments', 'fincare', 'nsdl jiffy', 'fino', 'fino payments', 'paytm payments', 'india post payments', 'jio payments', 'airtel payments', 'aditya birla payments', 'upi', 'wallet', 'qr code', 'scan and pay', 'virtual payment address', 'vpa', 'imps', 'neft', 'rtgs', 'aeps', 'bharat qr', 'upi id', 'upi pin', 'upi collect', 'upi pay', 'upi transfer', 'upi payment', 'upi withdrawal', 'upi deposit', 'upi refund', 'upi reversal', 'upi mandate', 'upi autopay', 'upi billpay', 'upi recharge', 'upi emi', 'upi installment', 'upi subscription', 'upi renewal'
                ],
                'weight': 0.9
            },
            'Mutual Funds & Stocks': {
                'keywords': [
                    'zerodha', 'groww', 'upstox', 'icici direct', 'hdfc securities', 'angel broking', 'motilal oswal', 'sharekhan', '5paisa', 'kotak securities', 'axis direct', 'sbi mutual fund', 'hdfc mutual fund', 'icici pru mf', 'axis mf', 'uti mf', 'franklin templeton', 'nippon india mf', 'mirae asset', 'motilal oswal mf', 'edelweiss mf', 'quantum mf', 'sbi securities', 'hdfc securities', 'icici direct', 'axis direct', 'kotak securities', 'angel one', 'upstox', 'zerodha', 'groww', '5paisa', 'sharekhan'
                ],
                'weight': 0.8
            },
            'Credit Cards': {
                'keywords': [
                    'hdfc', 'sbi', 'icici', 'axis', 'amex', 'kotak', 'rbl', 'indusind', 'yes bank', 'standard chartered', 'citi', 'hsbc', 'bob', 'idfc', 'federal', 'dcb', 'south indian bank', 'credit card', 'debit card', 'mastercard', 'visa', 'rupay', 'maestro', 'diners club', 'discover', 'platinum card', 'gold card', 'classic card', 'signature card', 'infinite card', 'world card', 'business card', 'corporate card', 'prepaid card', 'virtual card', 'forex card', 'travel card', 'fuel card', 'reward card', 'cashback card', 'lifetime free card', 'secured card', 'unsecured card', 'add-on card', 'supplementary card', 'contactless card', 'chip card', 'magstripe card', 'smart card', 'instant card', 'premium card', 'elite card', 'titanium card', 'prime card', 'select card', 'iconia card', 'regalia card', 'diners card', 'infinite card', 'world card', 'business card', 'corporate card', 'prepaid card', 'virtual card', 'forex card', 'travel card', 'fuel card', 'reward card', 'cashback card', 'lifetime free card', 'secured card', 'unsecured card', 'add-on card', 'supplementary card', 'contactless card', 'chip card', 'magstripe card', 'smart card', 'instant card', 'premium card', 'elite card', 'titanium card', 'prime card', 'select card', 'iconia card', 'regalia card', 'diners card'
                ],
                'weight': 0.8
            }
        }
        
        # Initialize variables for category scoring
        max_score = 0
        best_category = 'Other'
        
        # Score each category based on keyword matches
        for category, data in categories.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in description:
                    score += data['weight']
            
            # Update best category if current score is higher
            if score > max_score:
                max_score = score
                best_category = category
        
        return best_category

    def _process_text_chunk(self, chunk):
        # Process a chunk of text to extract transactions
        transactions = []
        # Add your transaction extraction logic here
        return transactions

    def _parse_kotak_pdf(self, text):
        import re
        lines = text.splitlines()
        joined_lines = []
        buffer = ""
        for line in lines:
            if re.match(r'^\d{2}-\d{2}-\d{4}', line):
                if buffer:
                    joined_lines.append(buffer.strip())
                buffer = line
            else:
                buffer += " " + line
        if buffer:
            joined_lines.append(buffer.strip())
        print("==== KOTAK JOINED LINES ====")
        for i, line in enumerate(joined_lines):
            print(f"{i}: {line}")
            if i > 20: break  # Only print the first 20 lines
        transactions = []
        # Regex for the table format you provided
        pattern = re.compile(
            r'^(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d,]+\.\d{2})\((Cr|Dr)\)\s+([\d,]+\.\d{2})\((Cr|Dr)\)$'
        )
        for line in joined_lines:
            match = pattern.search(line)
            if match:
                date, narration_chqref, amount, typ, balance, bal_type = match.groups()
                amount = float(amount.replace(',', ''))
                if typ == 'Dr':
                    amount = -amount
                transactions.append({
                    'date': date,
                    'description': narration_chqref.strip(),
                    'amount': amount,
                    'balance': float(balance.replace(',', ''))
                })
        return transactions

    def _parse_phonepe_pdf(self, text):
        transactions = []
        for line in text.splitlines():
            # Example: 01/05/2024, "Payment to XYZ", 500.00, DR, 4500.00
            parts = line.split(',')
            if len(parts) == 5:
                date, desc, amount, typ, balance = [p.strip() for p in parts]
                amount = float(amount)
                if typ == 'DR':
                    amount = -amount
                transactions.append({
                    'date': date,
                    'description': desc,
                    'amount': amount,
                    'balance': float(balance)
                })
        return transactions

    # ... rest of the existing methods ... 