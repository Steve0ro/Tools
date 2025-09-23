import requests
import sys
from urllib.parse import urlparse


def parse_github_url(url):
    parsed = urlparse(url)
    if parsed.hostname != "github.com":
        raise ValueError("URL must be a GitHub repository URL")
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL")
    owner = path_parts[0]
    repo = path_parts[1]
    return owner, repo


def get_default_branch(owner, repo):
    headers = {"Accept": "application/vnd.github.v3+json"}
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_url, headers=headers)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to get repository info: {
                response.status_code} - {response.text}"
        )
    repo_data = response.json()
    return repo_data["default_branch"]


def get_repo_tree(owner, repo, branch):
    headers = {"Accept": "application/vnd.github.v3+json"}
    branch_url = f"https://api.github.com/repos/{
        owner}/{repo}/branches/{branch}"
    response = requests.get(branch_url, headers=headers)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to get branch info: {
                response.status_code} - {response.text}"
        )
    branch_data = response.json()
    commit_sha = branch_data["commit"]["sha"]
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{
        commit_sha
    }?recursive=1"
    response = requests.get(tree_url, headers=headers)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to get tree: {response.status_code} - {response.text}"
        )
    tree_data = response.json()
    return tree_data["tree"]


def collect_paths(tree):
    files = []
    directories = []
    for item in tree:
        path = item["path"]
        if item["type"] == "blob":
            files.append("/" + path)
        elif item["type"] == "tree":
            directories.append("/" + path + "/")

    def path_depth(p):
        return p.count("/")

    files.sort(key=path_depth)
    directories.sort(key=path_depth)
    return files + directories


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python uri_maker.py <github_repo_url>")
        sys.exit(1)

    url = sys.argv[1]
    try:
        owner, repo = parse_github_url(url)
        branch = get_default_branch(owner, repo)
        tree = get_repo_tree(owner, repo, branch)
        paths = collect_paths(tree)
        with open("wordlist.txt", "w", encoding="UTF-8") as f:
            for path in paths:
                print(path)
                f.write(path + "\n")
        print("Wordlist saved..")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
