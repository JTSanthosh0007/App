import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { writeFile } from 'fs/promises';
import path from 'path';
import os from 'os';

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Create a temporary file
    const tempDir = os.tmpdir();
    const tempFilePath = path.join(tempDir, `statement-${Date.now()}.pdf`);
    
    // Write the uploaded file to the temporary location
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(tempFilePath, buffer);

    // Get the absolute path to the Python script
    const scriptPath = path.join(process.cwd(), 'scripts', 'statement_parser.py');

    // Run the Python script with detailed error handling
    const pythonProcess = spawn('python', [scriptPath, tempFilePath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    return new Promise<NextResponse>((resolve) => {
      let outputData = '';
      let errorData = '';

      pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
        console.error('Python script error:', data.toString());
      });

      pythonProcess.on('error', (error) => {
        console.error('Failed to start Python process:', error);
        resolve(
          NextResponse.json(
            { error: 'Failed to start analysis process' },
            { status: 500 }
          )
        );
      });

      pythonProcess.on('close', (code) => {
        // Clean up the temporary file
        writeFile(tempFilePath, '').catch(console.error);

        if (code !== 0) {
          console.error('Python script exited with code:', code);
          console.error('Error output:', errorData);
          
          // Parse the error message from the Python script
          let errorMessage = 'Analysis failed';
          try {
            const errorJson = JSON.parse(errorData);
            errorMessage = errorJson.error || errorData;
          } catch (e) {
            // If error output is not JSON, use it directly
            errorMessage = errorData.split('\n').pop() || errorData;
          }
          
          resolve(
            NextResponse.json(
              { 
                error: errorMessage,
                details: errorData,
                exitCode: code
              },
              { status: 500 }
            )
          );
          return;
        }

        try {
          const results = JSON.parse(outputData);
          console.log('Python script output:', results); // Add debug logging
          
          if (results.error) {
            resolve(
              NextResponse.json(
                { 
                  error: results.error,
                  details: results.error
                },
                { status: 500 }
              )
            );
            return;
          }
          
          // Ensure pageCount is included in the response
          const response = {
            ...results,
            pageCount: results.pageCount || 0
          };
          console.log('Sending response:', response); // Add debug logging
          resolve(NextResponse.json(response));
        } catch (e) {
          console.error('Failed to parse Python script output:', e);
          console.error('Raw output:', outputData);
          resolve(
            NextResponse.json(
              { 
                error: 'Failed to parse analysis results',
                details: `Error: ${e.message}\nOutput: ${outputData}`
              },
              { status: 500 }
            )
          );
        }
      });
    });
  } catch (error) {
    console.error('Error processing statement:', error);
    return NextResponse.json(
      { 
        error: 'Failed to process statement',
        details: error.message
      },
      { status: 500 }
    );
  }
} 