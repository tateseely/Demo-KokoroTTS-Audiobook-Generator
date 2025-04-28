import os
import re
import sys
import argparse
from pathlib import Path
from io import StringIO

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

# Example usage: python pdf-to-chapter-txt.py 'My Book.pdf'

def get_pdf_outline(pdf_path):
    """Extract the table of contents/outline from a PDF"""
    chapters = []
    
    with open(pdf_path, 'rb') as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)
        
        # Collect all pages and their PDF object IDs
        pages = list(PDFPage.create_pages(document))
        page_objids = [page.pageid for page in pages]  
        page_count = len(pages)
        
        # Check if outline exists
        if not document.catalog.get('Outlines'):
            print("No table of contents found. Treating entire PDF as one chapter.")
            return [("Chapter1", 0, page_count - 1)]
        
        # Get outlines
        outlines = document.get_outlines()
        if not outlines:
            print("No table of contents found. Treating entire PDF as one chapter.")
            return [("Chapter1", 0, page_count - 1)]
        
        chapter_data = []
        for entry in outlines:
            level, title, dest, a, se = entry
            if level > 1 or not title:
                continue
                
            clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            page_num = 0  # Default to first page
            
            if dest:
                try:
                    # Resolve different destination formats
                    if isinstance(dest, list):
                        # Array format: [page_ref, ...]
                        page_ref = dest[0]
                        target_objid = page_ref.objid
                    else:
                        # Named destination
                        target_objid = dest.dest.pageid
                    
                    # Find matching page index
                    page_num = page_objids.index(target_objid)
                except (AttributeError, ValueError, KeyError):
                    pass  # Fall back to default page 0
            
            chapter_data.append((clean_title, page_num))
        
        # Calculate end pages
        for i, (title, page_num) in enumerate(chapter_data):
            end_page = chapter_data[i+1][1] - 1 if i < len(chapter_data) - 1 else page_count - 1
            chapters.append((title, page_num, end_page))
            
        if not chapters:
            print("Could not parse table of contents properly. Treating entire PDF as one chapter.")
            return [("Chapter1", 0, page_count - 1)]
    
    return chapters

def extract_text_from_page_range(pdf_path, start_page, end_page):
    """Extract text from a range of pages using pdfminer.six"""
    # Create a new StringIO for each chapter extraction
    output = StringIO()
    
    with open(pdf_path, 'rb') as file:
        resource_manager = PDFResourceManager()
        device = TextConverter(resource_manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, device)
        
        # Get all pages but only process the ones in our range
        pages = list(PDFPage.get_pages(file))
        start_page = max(0, min(start_page, len(pages) - 1))
        end_page = max(0, min(end_page, len(pages) - 1))
        
        for i in range(start_page, end_page + 1):
            if i < len(pages):
                interpreter.process_page(pages[i])
        
        # Get the text and close resources
        text = output.getvalue()
        device.close()
        output.close()
    
    # Remove all line breaks
    text = text.replace("\n", " ").replace("\r", " ").replace("\f", " ")

    return text

def save_chapter_text(output_dir, chapter_title, chapter_text):
    """Save chapter text to a file"""
    chapter_file = os.path.join(output_dir, f"{chapter_title}.txt")
    with open(chapter_file, 'w', encoding='utf-8') as f:
        f.write(chapter_text)
    return chapter_file

def convert_pdf_to_chapter_files(pdf_path):
    """
    Main function to convert a PDF into separate chapter text files
    using pdfminer.six for better text extraction
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: File '{pdf_path}' does not exist.")
        return False
    
    output_dir = pdf_path.stem
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        chapters = get_pdf_outline(pdf_path)
        
        print(f"Found {len(chapters)} chapters in '{pdf_path.name}'")
        
        for i, (chapter_title, start_page, end_page) in enumerate(chapters):
            print(f"Processing chapter: {chapter_title} (pages {start_page}-{end_page})")
            
            # Extract text for this specific chapter only
            chapter_text = extract_text_from_page_range(pdf_path, start_page, end_page)
            
            # Save this chapter's text to its own file
            chapter_file = save_chapter_text(output_dir, chapter_title, chapter_text)
            print(f"Saved chapter to: {chapter_file}")
        
        print(f"Conversion complete! All chapters saved to directory: {output_dir}")
        return True
    
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert PDF book to chapter text files')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    args = parser.parse_args()
    
    success = convert_pdf_to_chapter_files(args.pdf_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())