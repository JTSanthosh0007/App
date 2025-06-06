import { NextRequest, NextResponse } from 'next/server';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import { writeFile } from 'fs/promises';
import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';

export async function POST(request: NextRequest): Promise<NextResponse> {
  let tempFilePath: string | null = null;
  let pythonProcess: ChildProcessWithoutNullStreams | null = null;

  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return NextResponse.json({ error: 'Only PDF files are supported' }, { status: 400 });
    }

    // Create temp directory if it doesn't exist
    const rootDir = process.cwd();
    const tempDir = path.join(rootDir, 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    // Create a temporary file path
    tempFilePath = path.join(tempDir, `${randomUUID()}.pdf`);

    // Convert File to Buffer and save it
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(tempFilePath, buffer);

    // Get the absolute path to the Python script
    const scriptPath = path.join(rootDir, 'api_statement_parser.py');
    
    // Check if the script exists
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Python script not found at ${scriptPath}`);
    }

    // Run the Python script
    pythonProcess = spawn('python', [scriptPath, tempFilePath]);

    return new Promise<NextResponse>((resolve) => {
      let result = '';
      let error = '';

      if (!pythonProcess) {
        resolve(NextResponse.json({ error: 'Failed to start Python process' }, { status: 500 }));
        return;
      }

      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
        console.log('Python script output:', data.toString());
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
        console.error('Python script error:', data.toString());
      });

      pythonProcess.on('close', (code) => {
        // Clean up the temporary file
        if (tempFilePath && fs.existsSync(tempFilePath)) {
          try {
            fs.unlinkSync(tempFilePath);
          } catch (e) {
            console.error('Error cleaning up temp file:', e);
          }
        }

        if (code !== 0) {
          resolve(NextResponse.json({ 
            error: error || 'Failed to analyze statement',
            details: {
              code,
              scriptPath,
              tempPath: tempFilePath
            }
          }, { status: 500 }));
          return;
        }

        try {
          const parsedResult = JSON.parse(result);
          resolve(NextResponse.json(parsedResult));
        } catch (e) {
          resolve(NextResponse.json({ 
            error: 'Invalid response from parser',
            details: {
              parseError: e.message,
              rawOutput: result
            }
          }, { status: 500 }));
        }
      });
    });
  } catch (error) {
    // Clean up resources in case of error
    if (pythonProcess) {
      pythonProcess.kill();
    }
    if (tempFilePath && fs.existsSync(tempFilePath)) {
      try {
        fs.unlinkSync(tempFilePath);
      } catch (e) {
        console.error('Error cleaning up temp file:', e);
      }
    }
    console.error('Error processing request:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error.message
    }, { status: 500 });
  }
} 