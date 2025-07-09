import requests
from bs4 import BeautifulSoup

A_PROMPTS = [
    "list files in the current directory",
    "print the current working directory",
    "show the current date and time",
    "display my username",
    "create a new empty file called test123.txt",
]

B_PROMPTS = [
    "Respond with a Windows command that lists all files in the current directory, and nothing else.",
    "Respond with a Windows command that prints the current working directory, and nothing else.",
    "Respond with a Windows command that shows the current date and time, and nothing else.",
    "Respond with a Windows command that displays my username, and nothing else.",
    "Respond with a Windows command that creates an empty file named test123.txt, and nothing else.",
]

TEST_URL = "http://127.0.0.1:5000/"


def submit_prompt(prompt):
    session = requests.Session()
    # Get the page to get cookies
    session.get(TEST_URL)
    resp = session.post(TEST_URL, data={"prompt": prompt})
    soup = BeautifulSoup(resp.text, "html.parser")
    command = soup.find("div", class_="command")
    output = soup.find("div", class_="output")
    return {
        "prompt": prompt,
        "command": command.text.strip() if command else None,
        "output": output.text.strip() if output else None,
        "success": bool(command and output)
    }


def ab_test():
    print("A/B Testing Agent Prompts...")
    print("A: Minimal | B: Structured\n")
    results = []
    for label, prompts in [("A", A_PROMPTS), ("B", B_PROMPTS)]:
        for prompt in prompts:
            result = submit_prompt(prompt)
            result["group"] = label
            results.append(result)
            print(f"[{label}] Prompt: {prompt}")
            print(f"    Command: {result['command']}")
            print(f"    Output: {result['output']}")
            print(f"    Success: {result['success']}")
            print("-")
    return results

if __name__ == "__main__":
    ab_test()
