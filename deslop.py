import argparse
import os
import re
import sys
import tiktoken

CHUNK_SIZE_IN_CHARACTERS = 30

def contains_css(text):
    css_patterns = [
        r'\s*[^{]+\s*{\s*[^}]+\s*}',  # Standard CSS rule
        r'[^:]+:[^;]+;',  # CSS property-value pair
        r'/\*!?[\s\S]*?\*/',  # CSS comment
        r'@[^{]+\{[^}]+\}',  # CSS at-rule
        r'\.[a-zA-Z0-9_-]+',  # Class selector
        r'#[a-zA-Z0-9_-]+',  # ID selector
        r'[a-zA-Z-]+\s*:',  # Property name followed by colon
        r':\s*[^;]+;',  # Property value
        r'--[a-zA-Z0-9-]+\s*:',  # CSS custom property
        r'var\s*\([^)]+\)',  # CSS var() function
        r'!important',  # !important declaration
        r'gradient\s*\([^)]+\)',  # gradient() function
        r'-(?:webkit|moz|ms|o)-',  # Vendor prefixes
        r'(?:background|color)(?:-[a-z]+)*\s*:',  # Background and color properties
        r'--[a-zA-Z0-9-]+(?:-[a-zA-Z0-9-]+)*\s*:',  # Extended CSS custom property pattern
        r'(?:normal|italic|oblique|inherit|initial|unset)\s+(?:normal|bold|bolder|lighter|[1-9]00|inherit|initial|unset)',  # Font shorthand start
        r'(?:[0-9]+(?:px|em|rem|%|vh|vw))',  # Size units
        r'(?:serif|sans-serif|monospace|cursive|fantasy|system-ui|ui-serif|ui-sans-serif|ui-monospace|ui-rounded)',  # Font families
        r'(?:\.[\w-]+\s*)+',  # Multiple chained class selectors
        r'(?:\.[\w-]+)+(?:\.[a-zA-Z][\w-]*)+',  # Complex chained class selectors
        r'\.use-media-queries',  # Edge case 1
        r'\.gt-xs',  # Edge case 2
    ]
    combined_pattern = '|'.join(css_patterns)
    return bool(re.search(combined_pattern, text, re.IGNORECASE | re.MULTILINE))

def chunk_data(unchunked_text):
    chunks = []
    for i in range(0, len(unchunked_text), CHUNK_SIZE_IN_CHARACTERS):
        chunks.append(unchunked_text[i:i + CHUNK_SIZE_IN_CHARACTERS])
    return chunks

def safe_file_operation(file_path, mode, operation):
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            return operation(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when accessing '{file_path}'.")
        sys.exit(1)
    except IOError as e:
        print(f"Error: An I/O error occurred with file '{file_path}': {e}")
        sys.exit(1)

def get_input(prompt):
    return input(prompt).strip()

def deslop_text(input_text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    original_tokens = len(encoding.encode(input_text))

    chunks = chunk_data(input_text)

    clean_chunks = []
    for i, chunk in enumerate(chunks):
        prev_chunk = chunks[i-1] if i > 0 else ""
        next_chunk = chunks[i+1] if i < len(chunks) - 1 else ""
        
        current_contains_css = contains_css(chunk)
        prev_contains_css = contains_css(prev_chunk)
        next_contains_css = contains_css(next_chunk)
        
        if not (current_contains_css and (prev_contains_css or next_contains_css)):
            clean_chunks.append(chunk)

    clean_text = "".join(clean_chunks)
    final_tokens = len(encoding.encode(clean_text))

    return clean_text, original_tokens, final_tokens

def main(input_file):
    _, input_filename = os.path.split(input_file)
    output_file = 'cleaned_' + input_filename
    
    print(f"Starting to process file: {input_file}")

    try:
        unchunked_text = safe_file_operation(input_file, "r", lambda f: f.read())
        print(f"Read {len(unchunked_text)} characters from input file")

        clean_text, original_tokens, final_tokens = deslop_text(unchunked_text)

        safe_file_operation(output_file, "w", lambda f: f.write(clean_text))

        print(f"Cleaned data written to {output_file}")
        print(f"Original text contained {original_tokens} tokens")
        print(f"Detected and removed {original_tokens - final_tokens} tokens of slop.")
    except UnicodeDecodeError:
        print(f"Error: Unable to decode the contents of '{input_file}'. Please ensure it's a valid text file.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean web content from text files.")
    parser.add_argument("input_file", nargs='?', help="Path to the input file")
    args = parser.parse_args()

    if not args.input_file:
        print("Some arguments are missing. Please provide them interactively.")
        input_file = args.input_file or get_input("Enter input file path: ")
    else:
        input_file = args.input_file

    main(input_file)