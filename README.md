![Banner](banner.png)

# file-content-obfuscator
Applies basic obfuscation techniques (e.g., substitution ciphers, character shuffling) to a file's content, making it less readable without significantly altering functionality. Primarily for protecting intellectual property in scripts and configuration files. - Focused on File operations and analysis

## Install
`git clone https://github.com/ShadowStrikeHQ/file-content-obfuscator`

## Usage
`./file-content-obfuscator [params]`

## Parameters
- `-h`: Show help message and exit
- `-s`: Enable substitution cipher obfuscation.
- `-r`: Enable character shuffling obfuscation.
- `-k`: Key used for the substitution cipher. Default is 42.
- `--seed`: Seed for character shuffling. When none is given, one is generated and printed in the run log line.
- `--reverse`: Reverse a shuffle made with `-r` and the same `--seed`, restoring the original order.
- `-l`: Set the logging level.

## Notes
- The output file must not be the input file. A run whose output path resolves to the input file is refused at exit 1, including the same path written with a `./` prefix or through a symlink.
- An empty input file exits 1 with a plain line and is not reported as a successful run.
- Shuffling is recoverable only with its seed. Reversal needs the seed: run with `-r --reverse --seed N`, where N is the seed from the shuffling run. Without the seed, the shuffled order is not recoverable.
- The substitution method is a plain shift of each character by the key. Anyone who knows or guesses the key can reverse it, so it is light obfuscation, not strong encryption. A key that would move a character in the file outside the valid character range is refused at exit 1 with the reason, before any output is written.

## License
Copyright (c) ShadowStrikeHQ
