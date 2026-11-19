import glob
import json
import sys


def differing_keys(before, after):
    """Return the keys whose values differ between two dicts.

    None (Terraform's null) is treated as an empty dict.
    Anything else that isn't a dict raises ValueError.
    """
    before = {} if before is None else before
    after = {} if after is None else after

    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ValueError(
            f"expected dicts, got {type(before).__name__} and {type(after).__name__}"
        )

    return {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}


def has_unknown(node):
    """True if an after_unknown node marks anything as 'known after apply'.

    after_unknown mirrors the shape of the resource: a leaf is True/False,
    but nested attributes are dicts or lists, so we search recursively.
    """
    if node is True:
        return True
    if isinstance(node, dict):
        return any(has_unknown(v) for v in node.values())
    if isinstance(node, list):
        return any(has_unknown(v) for v in node)
    return False


def update_problems(change):
    """Return reasons an 'update' is not allowed (empty list = fine)."""
    before = change.get("before")
    after = change.get("after")
    unknown = {} if change.get("after_unknown") is None else change["after_unknown"]

    if not all(isinstance(x, dict) for x in (before, after, unknown)):
        raise ValueError("update needs 'before', 'after' and 'after_unknown' objects")

    problems = []
    for attr in sorted(before.keys() | after.keys() | unknown.keys()):
        if attr != "tags":
            if has_unknown(unknown.get(attr)):
                problems.append(
                    f"'{attr}' is computed at apply time and cannot be verified "
                    f"(only tags may change)"
                )
            elif before.get(attr) != after.get(attr):
                problems.append(f"changes '{attr}' (only tags may change)")
            continue

        # --- the tags attribute: inspect tag by tag ---
        tags_unknown = unknown.get("tags")
        if tags_unknown is True:
            problems.append("'tags' is unknown until apply, so which tags change cannot be verified")
            continue
        if tags_unknown is None or tags_unknown is False:
            tags_unknown = {}
        if not isinstance(tags_unknown, dict):
            raise ValueError(f"unexpected after_unknown for tags: {type(tags_unknown).__name__}")

        unknown_tags = {k for k, v in tags_unknown.items() if has_unknown(v)}
        known_changes = differing_keys(before.get("tags"), after.get("tags")) - unknown_tags

        for tag in sorted(known_changes - {"GitCommitHash"}):
            problems.append(f"changes tag '{tag}' (only GitCommitHash may change)")
        for tag in sorted(unknown_tags - {"GitCommitHash"}):
            problems.append(f"tag '{tag}' is computed at apply time and cannot be verified")

    return problems


def check_file(path):
    """Print a verdict for one plan file. Return True if safe to apply."""
    print(f"\n=== {path} ===")

    try:
        with open(path) as f:
            plan = json.load(f)
    except FileNotFoundError:
        print("DO NOT PROCEED - file not found.")
        return False
    except json.JSONDecodeError as err:
        print(f"DO NOT PROCEED - file is not valid JSON ({err}).")
        print(f"If it is a binary plan, convert it first: terraform show -json {path} > plan.json")
        return False

    if not isinstance(plan, dict):
        print("DO NOT PROCEED - plan JSON is not an object.")
        return False

    blocked = False
    for rc in plan.get("resource_changes", []):
        address = rc["address"]
        change = rc["change"]
        actions = change["actions"]

        if actions in (["create"], ["no-op"], ["read"]):
            continue                                  # always fine
        elif actions == ["update"]:
            try:
                problems = update_problems(change)
            except ValueError as err:
                problems = [f"could not validate change ({err})"]
        else:                                         # delete, replace, etc.
            problems = [f"action {actions} is not allowed"]

        for problem in problems:
            print(f"  {address}: {problem}")
            blocked = True

    if blocked:
        print("DO NOT PROCEED - revert the changes listed above and re-plan.")
    else:
        print("PROCEED")
    return not blocked


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("*.tfplan"))
    if not files:
        print("No plan files found.")
        sys.exit(1)

    results = [check_file(f) for f in files]
    sys.exit(0 if all(results) else 1)