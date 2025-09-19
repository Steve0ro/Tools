# Bitdiff

HUGE thanks to Sammy K.
- This tool was built off of his tool [diffbits](https://github.com/samyk/samytools/blob/master/diffbits)
- Yes, this tool was 100% vibe-coded. No shame in my game, great learning experience


bitdiff is a command-line tool written in Nim that compares two groups of data (binary, hexadecimal, or ASCII text) and highlights similarities and differences between them. It reads input from a file or STDIN, processes it based on specified flags, and outputs a color-coded comparison showing common bits/characters, differences, and group-specific matches. The program is designed to handle binary, hex, or ASCII input, with flexible options for controlling how the data is interpreted and displayed.

## Features:

Input Formats: Supports binary (0s and 1s), hexadecimal (0-9, a-f, A-F), or ASCII text.

Comparison: Compares two groups of equal-length lines, separated by a blank line in the input.
Output: Displays data rows, a middle row with comparison symbols (= for common, X for differences, ^ or v for group-specific matches, - for unmatched), and a bottom row with position indices (0–7, cycling).
Color Coding: Uses ANSI colors to highlight differences (red/magenta), common bits (green), group-specific matches (cyan), and position markers (bold/yellow).
Comment Support: Preserves and displays comments (starting with #) from the input.
Error Handling: Silently skips invalid rows (e.g., inconsistent lengths) and exits gracefully on empty or invalid input.

## Installation

Ensure you have Nim installed (version 2.2.4 or later recommended).

Save the bitdiff.nim source file in your working directory.

Compile the program:

```bash
nim c bitdiff.nim
```

This generates an executable in the current directory.

## Usage

```bash
bitdiff [-v] [-n] [-h] <file>
```

Run with a file: nim r bitdiff.nim data.txt
Run with STDIN: cat data.txt | nim r bitdiff.nim

Use flags to modify behavior (see below).
If no file is provided and STDIN is a terminal (not piped), the program requires a flag (-v, -n, or -h) or it displays usage and exits.

## Flags

The program supports three flags to control input processing and output format:

-v (Verbose):

Displays the original input lines alongside the processed data (binary or raw).
Useful for seeing the raw input (e.g., Hello or 4A3F) next to its processed form.

Example:

```bash
nim r bitdiff.nim -v data.txt
```
-n (No Conversion):

Treats input as raw text, comparing characters directly without converting to binary or interpreting as hex.

Applies to any input (binary, hex, ASCII), treating each character as a single unit.



Example:

```bash
nim r bitdiff.nim -n data.txt
```

-h (Hex Mode):

Treats input as raw hexadecimal characters (0-9, a-f, A-F), comparing them directly without binary conversion.

If the input isn’t valid hex, it’s treated as raw text (similar to -n).

Example:

```bash
nim r bitdiff.nim -h data.txt
```

No Flags (Default Mode):

Converts input to binary based on its format:

Binary (0s, 1s, spaces, _): Used as-is.
Hex (0-9, a-f, A-F, spaces, _): Converted to binary (e.g., 4A to 01001010).
ASCII: Converted to 8-bit binary per character (e.g., H to 01001000).

Example:

```bash
nim r bitdiff.nim data.txt
```

## Input Format

Input consists of two groups of equal-length lines, separated by a blank line.
Lines can be binary, hex, or ASCII, with optional comments starting with #.

Example data.txt:
```c
1010 # First binary pattern
1100 # Second binary pattern

1001 # Third binary pattern
1110 # Fourth binary pattern
```

or for hex:

```c
4A3F # Hex pattern 1
4B2E # Hex pattern 2

4C1D # Hex pattern 3
4D0C # Hex pattern 4
```

```c
or for ASCII:

Hello # Greeting 1
Helio # Greeting 2

Hella # Greeting 3
Helix # Greeting 4
```

Output Format:

Data Rows: Each line of input is displayed (as binary in default mode, raw with -n or -h). With -v, the original line is shown alongside.

Middle Row: Shows comparison symbols:

= (green): Bits/characters common across all rows in both groups.
X (blue): Bits/characters that differ between groups but are consistent within each group.
^ or v (cyan): Bits/characters common within the first (^) or second (v) group but not across both.
- (no color): Non-binary or unmatched positions.
Bottom Row: Shows position indices (0–7, cycling), with 0 in bold and 4 in yellow.

Comments are displayed after each row if present.

Error Handling:

Inconsistent Lengths: Rows with lengths not matching the first row are silently skipped, and the program processes only valid rows. If no valid rows remain, it exits silently.

File Errors: If the input file cannot be read, the program exits silently.

Empty Input: Exits silently if no input is provided or after filtering invalid rows.

Requirements:

Nim compiler (version 2.2.4 or later).

A terminal supporting ANSI escape codes for color output (e.g., xterm, gnome-terminal).

Linux or Unix-like system (uses posix module for isatty).

Notes:

The program is a Nim port of a Perl script with similar functionality.
The -h flag expects valid hex input (0-9, a-f, A-F); non-hex input is treated as raw text, similar to -n.

For large ASCII inputs, default mode (no flags) produces long binary outputs (8 bits per character), so use -n or -h for shorter comparisons.

License

This project is unlicensed; use it at your own discretion.
