import argparse
import logging
import os
import random
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Obfuscates the content of a file.")
    parser.add_argument("input_file", help="The path to the input file.")
    parser.add_argument("output_file", help="The path to the output (obfuscated) file.")
    parser.add_argument("-s", "--substitution", action="store_true", help="Enable substitution cipher obfuscation.")
    parser.add_argument("-r", "--shuffle", action="store_true", help="Enable character shuffling obfuscation.")
    parser.add_argument("-k", "--key", type=int, default=42, help="Key used for the substitution cipher. Default is 42.")
    parser.add_argument("-l", "--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")
    return parser

def substitute_chars(content, key):
    """
    Applies a substitution cipher to the content.

    Args:
        content (str): The content to obfuscate.
        key (int): The substitution key.

    Returns:
        str: The obfuscated content.
    """
    obfuscated_content = ""
    for char in content:
        obfuscated_content += chr(ord(char) + key)  # Simple substitution
    return obfuscated_content

def shuffle_chars(content):
    """
    Shuffles the characters in the content.

    Args:
        content (str): The content to obfuscate.

    Returns:
        str: The obfuscated content.
    """
    content_list = list(content)
    random.shuffle(content_list)
    return ''.join(content_list)


def obfuscate_file(input_file_path, output_file_path, substitution=False, shuffle=False, key=42):
    """
    Obfuscates the content of a file using substitution and/or shuffling.

    Args:
        input_file_path (str): Path to the input file.
        output_file_path (str): Path to the output file.
        substitution (bool): Whether to use substitution cipher.
        shuffle (bool): Whether to shuffle characters.
        key (int): Key to use for substitution cipher.

    Raises:
        FileNotFoundError: If the input file does not exist.
        IOError: If there is an error reading or writing files.
        ValueError: If no obfuscation method is selected.
    """
    try:
        input_file_path = Path(input_file_path)
        output_file_path = Path(output_file_path)

        if not input_file_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file_path}")

        if not substitution and not shuffle:
            raise ValueError("No obfuscation method selected.  Use -s or -r to enable.")

        with open(input_file_path, 'r') as infile:
            content = infile.read()

        obfuscated_content = content

        if substitution:
            obfuscated_content = substitute_chars(obfuscated_content, key)
            logging.info("Applied substitution cipher.")

        if shuffle:
            obfuscated_content = shuffle_chars(obfuscated_content)
            logging.info("Applied character shuffling.")

        with open(output_file_path, 'w') as outfile:
            outfile.write(obfuscated_content)

        logging.info(f"Obfuscated file saved to: {output_file_path}")

    except FileNotFoundError as e:
        logging.error(str(e))
        raise
    except IOError as e:
        logging.error(f"IOError: {e}")
        raise
    except ValueError as e:
        logging.error(str(e))
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise


def main():
    """
    Main function to parse arguments and run the obfuscation process.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        logging.getLogger().setLevel(args.log_level)
    except ValueError:
        logging.error("Invalid log level specified.")
        sys.exit(1)

    try:
        obfuscate_file(
            args.input_file,
            args.output_file,
            substitution=args.substitution,
            shuffle=args.shuffle,
            key=args.key
        )
    except FileNotFoundError:
        sys.exit(1)
    except IOError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()