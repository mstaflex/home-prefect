#!/usr/bin/env python3
"""Pre-commit hook: ensure sensitive Ansible variables are vault-encrypted."""

import re
import sys

# Variable name patterns that must never appear as plaintext
SENSITIVE_PATTERNS = re.compile(
    r"^\s*([\w]+):\s+(?!null\b)(?!\{\{)(?!\[)(?!true\b)(?!false\b)(.+)$"
)

SENSITIVE_NAMES = re.compile(
    r"(private_key|password|secret|token|api_key|psk|passphrase)",
    re.IGNORECASE,
)

VAULT_MARKER = "!vault"


def check_file(path: str) -> list[str]:
    errors = []
    with open(path) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        m = SENSITIVE_PATTERNS.match(line)
        if m and SENSITIVE_NAMES.search(m.group(1)):
            value = m.group(2).strip()
            if not value.startswith(VAULT_MARKER):
                errors.append(f"{path}:{i + 1}: '{m.group(1)}' is not vault-encrypted")
        i += 1

    return errors


def main(files: list[str]) -> int:
    all_errors = []
    for path in files:
        all_errors.extend(check_file(path))

    if all_errors:
        print("ERROR: Unencrypted sensitive variables found:")
        for err in all_errors:
            print(f"  {err}")
        print("\nEncrypt them with: ansible-vault encrypt_string --name '<var>' '<value>'")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
