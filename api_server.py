from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from statement_parser import StatementParser
import io

app = FastAPI()

# Enable CORS with simpler configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileObject:
    def __init__(self, filename, content):
        self.name = filename
        self._content = content

    def read(self, *args):
        return self._content

@app.post("/analyze")
async def analyze_statement(
    file: UploadFile = File(...),
    platform: str = Form(...)
):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read the file content
        content = await file.read()
        
        # Create a proper file-like object
        file_obj = FileObject(file.filename, content)
        
        try:
            # Parse the statement
            parser = StatementParser(file_obj)
            df = parser.parse()
            
            # Convert to dictionary format
            transactions = df.to_dict('records')
            
            # Calculate summary statistics
            total_spent = sum(t['amount'] for t in transactions if t['amount'] < 0)
            total_received = sum(t['amount'] for t in transactions if t['amount'] > 0)
            
            # Calculate category breakdown
            category_breakdown = {}
            for t in transactions:
                if t['amount'] < 0:  # Only consider spending
                    category = t['category']
                    category_breakdown[category] = category_breakdown.get(category, 0) + t['amount']
            
            return {
                "transactions": transactions,
                "totalSpent": total_spent,
                "totalReceived": total_received,
                "categoryBreakdown": category_breakdown
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 