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
    parser.add_argument("--seed", type=int, default=None, help="Seed for character shuffling. When none is given, one is generated and printed in the run log line.")
    parser.add_argument("--reverse", action="store_true", help="Reverse a shuffle made with -r and the same --seed, restoring the original order.")
    parser.add_argument("-l", "--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")
    return parser

# A flat shift of every code point, with no wraparound. Undoing it is the
# same operation with the negated key, which the help text never says;
# anyone reversing a substituted file has to know to pass -k with the
# opposite sign. The range precheck in obfuscate_file exists because a
# shift that leaves the Unicode range has no character to land on.
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

# Shuffle and unshuffle each rebuild the same index permutation from the
# seed. That only inverts correctly when the content length is also the
# same, because the permutation is over positions. Reversing a file of a
# different length runs without error and produces scrambled text, with
# no signal that the length was wrong.
def shuffle_chars(content, seed):
    rng = random.Random(seed)
    indices = list(range(len(content)))
    rng.shuffle(indices)
    return ''.join(content[i] for i in indices)


def unshuffle_chars(content, seed):
    rng = random.Random(seed)
    indices = list(range(len(content)))
    rng.shuffle(indices)
    # The inverse places each shuffled character back at the position it was
    # taken from. shuffle_chars gathered content[i] in permuted order, so
    # this loop walks the same permutation in the opposite direction.
    restored = [''] * len(content)
    for new_pos, old_pos in enumerate(indices):
        restored[old_pos] = content[new_pos]
    return ''.join(restored)


def obfuscate_file(input_file_path, output_file_path, substitution=False, shuffle=False, key=42, seed=None, reverse=False):
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

        if os.path.realpath(input_file_path) == os.path.realpath(output_file_path):
            raise ValueError(f"Refusing to overwrite the input file: {output_file_path}")

        if reverse and not shuffle:
            raise ValueError("--reverse requires -r (shuffle) and the --seed used to shuffle.")

        if not substitution and not shuffle:
            raise ValueError("No obfuscation method selected.  Use -s or -r to enable.")

        # The file is read as text in the platform default encoding. A binary
        # file can raise UnicodeDecodeError here, which is a ValueError, so it
        # surfaces as the generic value error path in main, exit 1.
        with open(input_file_path, 'r') as infile:
            content = infile.read()

        if not content:
            raise ValueError("No content to obfuscate: input file is empty.")

        if substitution:
            if content:
                highest = max(ord(c) for c in content)
                lowest = min(ord(c) for c in content)
                # Only the extreme characters are checked, which is enough: every other
                # character sits between them, so if the extremes stay inside the valid
                # range after the shift, all of them do. Checking first also means a bad
                # key fails before any output exists, not halfway through building it.
                if highest + key > 0x10FFFF or lowest + key < 0:
                    raise ValueError(
                        f"Substitution key {key} is out of range for this content: "
                        f"it would move a character outside the valid range 0 to 1114111."
                    )

        obfuscated_content = content

        if substitution:
        # Order is fixed: substitution first, shuffle second. A combined run is
        # therefore reversed in the opposite order, unshuffle with --reverse
        # first and then a substitution pass with the negated key. --reverse
        # alone does not touch substituted text.
            obfuscated_content = substitute_chars(obfuscated_content, key)
            logging.info("Applied substitution cipher.")

        if shuffle:
            if seed is None:
                if reverse:
                    raise ValueError("Reversing a shuffle requires the --seed used to shuffle.")
                seed = random.SystemRandom().randrange(0, 2**31)
            if reverse:
                obfuscated_content = unshuffle_chars(obfuscated_content, seed)
                logging.info(f"Reversed character shuffling with seed: {seed}")
            else:
                obfuscated_content = shuffle_chars(obfuscated_content, seed)
                logging.info(f"Applied character shuffling with seed: {seed}")

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
            key=args.key,
            seed=args.seed,
            reverse=args.reverse
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