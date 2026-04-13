"""Generate spec/requirements.json from spec YAML files.

Reads all spec YAML files, collects requirement metadata, and writes
a machine-readable JSON file that conformance generators can consume
instead of hardcoding requirement IDs.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_spec import generate_requirements_data


def main():
    """Generate requirements.json from spec YAML files."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_dir = os.path.join(repo_root, "spec")
    output_path = os.path.join(spec_dir, "requirements.json")

    data = generate_requirements_data(spec_dir)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Generated {output_path}")
    print(f"  spec_version: {data['spec_version']}")
    print(f"  requirements: {len(data['requirements'])}")


if __name__ == "__main__":
    main()
