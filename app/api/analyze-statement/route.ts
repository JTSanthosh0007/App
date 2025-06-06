import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Forward the file to the Render backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL + '/analyze-statement'; // Use the environment variable
    
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      body: backendFormData,
    });

    const backendData = await backendResponse.json();

    if (!backendResponse.ok) {
      console.error('Backend error:', backendData);
      return NextResponse.json(backendData, { status: backendResponse.status });
    }

    return NextResponse.json(backendData);

  } catch (error: any) {
    console.error('Error in frontend API route:', error);
    return NextResponse.json(
      { 
        error: 'Failed to process statement via backend',
        details: error.message
      },
      { status: 500 }
    );
  }
} 