"""
Script to convert test text files to PDF format.
Requires: pip install reportlab
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def text_to_pdf(text_file: Path, output_pdf: Path):
    """Convert a text file to PDF."""
    # Read text file
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create PDF
    c = canvas.Canvas(str(output_pdf), pagesize=letter)
    width, height = letter
    
    # Set font and margins
    c.setFont("Helvetica", 10)
    margin = inch
    x = margin
    y = height - margin
    line_height = 12
    
    # Split text into lines and write
    lines = text.split('\n')
    for line in lines:
        if y < margin:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 10)
        
        # Handle long lines (wrap if needed)
        if len(line) > 80:
            words = line.split(' ')
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + " "
                else:
                    if current_line:
                        c.drawString(x, y, current_line.strip())
                        y -= line_height
                    current_line = word + " "
            if current_line:
                c.drawString(x, y, current_line.strip())
                y -= line_height
        else:
            c.drawString(x, y, line)
            y -= line_height
    
    c.save()
    print(f"Created: {output_pdf}")

def main():
    """Convert all text files to PDFs."""
    script_dir = Path(__file__).parent
    
    text_files = [
        "sample_witness_statement.txt",
        "sample_medical_report.txt",
        "sample_fir.txt",
        "sample_police_memo.txt",
    ]
    
    for text_file in text_files:
        text_path = script_dir / text_file
        if text_path.exists():
            pdf_path = script_dir / text_file.replace('.txt', '.pdf')
            text_to_pdf(text_path, pdf_path)
        else:
            print(f"Warning: {text_file} not found")
    
    print("\n✅ All PDFs created successfully!")
    print("\nYou can now upload these PDF files to the system.")

if __name__ == "__main__":
    main()

