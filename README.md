# deslop - Clean your web-scraped content

deslop is a python script that removes CSS and other unnecessary content from web-scraped text.

## Requirements
- Python 3.6+
- `tiktoken` library

## Installation
1. Clone this repository or download the `deslop.py` file.
2. Install the `tiktoken` library using pip: `pip install tiktoken`

## Usage

To use deslop, you can either run the script directly or use it as a module in your own code.

### Running the script
1. Open a terminal or command prompt.
2. Navigate to the directory where you saved the `deslop.py` file.
3. Run the script by typing `python deslop.py [input_file]` and pressing Enter.
   - If you don't provide an input file, the script will prompt you to enter the path to the input file.
4. The script will create a new file with the prefix `cleaned_` added to the original filename. It will also display:

- The number of characters read from the input file
- The path of the output file
- The number of tokens in the original text
- The number of tokens removed as "slop"

### Using the script as a module
1. Import the `deslop` module in your code.
2. Call the `deslop_text` function with the input text as an argument.
3. The function will return a tuple containing the cleaned text, the original number of tokens, and the number of tokens removed as "slop".

## Example

```python
import deslop

input_text = "This is some text with CSS and other unnecessary content."
cleaned_text, original_tokens, final_tokens = deslop.deslop_text(input_text)

print(f"Cleaned text: {cleaned_text}")
print(f"Original tokens: {original_tokens}")
print(f"Final tokens: {final_tokens}")
```

## Customization

You can increase the sensitivity of the script by decreasing the value of the `CHUNK_SIZE_IN_CHARACTERS` constant in the `deslop.py` file. Decreasing this value will result in more aggressive cleaning, but it may also remove more content.