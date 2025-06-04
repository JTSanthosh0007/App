import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import { writeFile, unlink } from 'fs/promises'
import path from 'path'
import { v4 as uuidv4 } from 'uuid'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const password = formData.get('password') as string

    if (!file || !password) {
      return NextResponse.json(
        { error: 'File and password are required' },
        { 
          status: 400,
          headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Content-Type-Options': 'nosniff',
            'Cache-Control': 'no-store, max-age=0'
          }
        }
      )
    }

    // Create temporary file paths
    const tempId = uuidv4()
    const inputPath = path.join(process.cwd(), `temp_${tempId}_input.pdf`)
    const outputPath = path.join(process.cwd(), `temp_${tempId}_output.pdf`)

    // Write uploaded file to disk
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    await writeFile(inputPath, buffer)

    // Run Python script to unlock PDF
    const pythonProcess = spawn('python', [
      path.join(process.cwd(), 'scripts', 'unlock_pdf.py'),
      inputPath,
      outputPath,
      password
    ])

    const result = await new Promise((resolve, reject) => {
      let errorOutput = ''

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString()
      })

      pythonProcess.on('close', async (code) => {
        try {
          // Clean up input file
          await unlink(inputPath)

          if (code !== 0) {
            reject(new Error(`Python process failed: ${errorOutput}`))
            return
          }

          // Read the unlocked PDF
          const unlockedPdf = await require('fs').promises.readFile(outputPath)
          
          // Clean up output file
          await unlink(outputPath)

          resolve(unlockedPdf)
        } catch (err) {
          reject(err)
        }
      })
    })

    return new NextResponse(result as Buffer, {
      headers: {
        'Content-Type': 'application/pdf; charset=utf-8',
        'Content-Disposition': `attachment; filename="${file.name.replace('.pdf', '_unlocked.pdf')}"`,
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-store, max-age=0'
      },
    })
  } catch (error) {
    console.error('Error unlocking PDF:', error)
    return NextResponse.json(
      { error: 'Failed to unlock PDF' },
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-Content-Type-Options': 'nosniff',
          'Cache-Control': 'no-store, max-age=0'
        }
      }
    )
  }
} 