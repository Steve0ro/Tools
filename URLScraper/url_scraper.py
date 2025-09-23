#!/usr/bin/env python3
"""
uri_maker.py

Create a wordlist of repository/file paths from:
 - a local directory tree (preferred by default if the argument points to disk)
 - OR an optional GitHub repository URL (uses GitHub API)

Features:
 - If the argument is an existing local path, builds the list from the filesystem (no network).
 - Preserves the same path-style output as your original script:
      files -> "/path/to/file"
      directories -> "/path/to/dir/"
 - Options for recursion, output filename, sorting (depth / alpha), and local-only mode.
 - Robust error messages and UTF-8-safe file writing.
"""

from urllib.parse import urlparse
import os
import sys
import argparse
import requests
from typing import List, Tuple


def parse_github_url(url: str) -> Tuple[str, str]:
    parsed = urlparse(url)
    if parsed.hostname != "github.com":
        raise ValueError("URL must be a GitHub repository URL (github.com)")
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL; expected https://github.com/owner/repo"
        )
    owner = path_parts[0]
    repo = path_parts[1]
    return owner, repo


def get_default_branch(owner: str, repo: str) -> str:
    headers = {"Accept": "application/vnd.github.v3+json"}
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(repo_url, headers=headers)
    if resp.status_code != 200:
        raise ValueError(
            f"Failed to get repository info: {resp.status_code} - {resp.text}"
        )
    return resp.json().get("default_branch")


def get_repo_tree(owner: str, repo: str, branch: str) -> List[dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    branch_url = f"https://api.github.com/repos/{
        owner}/{repo}/branches/{branch}"
    resp = requests.get(branch_url, headers=headers)
    if resp.status_code != 200:
        raise ValueError(f"Failed to get branch info: {
                         resp.status_code} - {resp.text}")
    commit_sha = resp.json()["commit"]["sha"]
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{
        commit_sha
    }?recursive=1"
    resp = requests.get(tree_url, headers=headers)
    if resp.status_code != 200:
        raise ValueError(f"Failed to get tree: {
                         resp.status_code} - {resp.text}")
    return resp.json().get("tree", [])


def collect_paths_from_tree(tree: List[dict]) -> List[str]:
    files = []
    directories = []
    for item in tree:
        path = item["path"]
        if item["type"] == "blob":
            files.append("/" + path)
        elif item["type"] == "tree":
            directories.append("/" + path + "/")

    def path_depth(p: str) -> int:
        return p.count("/")

    files.sort(key=path_depth)
    directories.sort(key=path_depth)
    return files + directories


def collect_paths_from_local(base_dir: str, recursive: bool) -> List[str]:
    base_dir = os.path.abspath(base_dir)
    if not os.path.isdir(base_dir):
        raise ValueError(f"Local path is not a directory: {base_dir}")

    files = []
    directories = set()

    if recursive:
        for root, dirnames, filenames in os.walk(base_dir):
            rel_root = os.path.relpath(root, base_dir)
            if rel_root == ".":
                rel_root = ""
            else:
                rel_root = rel_root.replace("\\", "/")

            for d in dirnames:
                dirpath = os.path.join(rel_root, d).replace("\\", "/")
                directories.add("/" + dirpath + "/")

            for fn in filenames:
                filepath = os.path.join(rel_root, fn).replace("\\", "/")
                files.append("/" + filepath)
    else:
        for entry in os.listdir(base_dir):
            full = os.path.join(base_dir, entry)
            rel = entry.replace("\\", "/")
            if os.path.isdir(full):
                directories.add("/" + rel + "/")
            elif os.path.isfile(full):
                files.append("/" + rel)

    def path_depth(p: str) -> int:
        return p.count("/")

    files.sort(key=path_depth)
    sorted_dirs = sorted(list(directories), key=path_depth)
    return files + sorted_dirs


def write_wordlist(paths: List[str], out_file: str, encoding: str = "utf-8"):
    with open(out_file, "w", encoding=encoding, errors="replace") as f:
        for p in paths:
            print(p)
            f.write(p + "\n")
    print(f"Wordlist saved to {out_file} ({len(paths)} entries).")


def main():
    parser = argparse.ArgumentParser(
        description="Create a wordlist of paths from a local directory or GitHub repo."
    )
    parser.add_argument(
        "source",
        help="Local directory path OR GitHub repo URL (https://github.com/owner/repo)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="wordlist.txt",
        help="Output file (default: wordlist.txt)",
    )
    parser.add_argument(
        "-n",
        "--non-recursive",
        action="store_true",
        help="Do not recurse into subdirectories (local mode only)",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Treat the source as local; do not attempt GitHub fetches",
    )
    parser.add_argument(
        "--allow-github",
        action="store_true",
        help="Allow GitHub network fetches even if source looks like local path",
    )
    args = parser.parse_args()

    source = args.source
    out_file = args.output
    recursive = not args.non_recursive

    try:
        if os.path.exists(source) and os.path.isdir(source) and not args.allow_github:
            paths = collect_paths_from_local(source, recursive)
            write_wordlist(paths, out_file)
            return
        if args.local_only:
            if not (os.path.exists(source) and os.path.isdir(source)):
                print(
                    "Error: --local-only specified but source is not an existing directory."
                )
                sys.exit(1)
            paths = collect_paths_from_local(source, recursive)
            write_wordlist(paths, out_file)
            return

        try:
            owner, repo = parse_github_url(source)
        except ValueError:
            if os.path.exists(source) and os.path.isdir(source):
                paths = collect_paths_from_local(source, recursive)
                write_wordlist(paths, out_file)
                return
            print(
                "Error: source is neither an existing directory nor a valid GitHub repository URL."
            )
            sys.exit(1)

        branch = get_default_branch(owner, repo)
        tree = get_repo_tree(owner, repo, branch)
        paths = collect_paths_from_tree(tree)
        write_wordlist(paths, out_file)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error while contacting GitHub: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
