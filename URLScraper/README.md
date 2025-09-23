A Python script to generate a wordlist of file and directory paths from a GitHub repository.

Purpose:

This tool fetches the file and directory structure of a public GitHub repository using the GitHub API and creates a wordlist of absolute paths, with files listed first, followed by directories, sorted by path depth.

Requirements:
Python 3.x
requests library (pip install requests)

Usage:

Run the script with a GitHub repository URL:
python3 url_scraper.py https://github.com/danielmiessler/SecLists

Output:

Prints paths to the console (e.g., /README.md, /Discovery/DNS/, etc.).
Saves the wordlist to wordlist.txt in the current directory.

Example:

For https://github.com/danielmiessler/SecLists, the output might include:
```bash
/README.md
/LICENSE
/Discovery/DNS/dnsmap.txt
/Discovery/
/Discovery/DNS/
```

Notes:

Uses the GitHub API (unauthenticated, 60 requests/hour limit).
Handles the repository's default branch dynamically (e.g., main or master).
For private repositories or higher rate limits, add a GitHub Personal Access Token to the script.

Limitations:

Large repositories may hit API limits or return truncated trees.
Requires a valid GitHub repository URL.
