import core
import argparse
import logging
import sys

def execute_command(profile_name, fix_opt):
    if(fix_opt == "tags"):
        fix_tags = core.tags.Fix(profile_name)
        fix_tags.fix()
    else:
        logging.error("Error: Uknow option")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    parser = argparse.ArgumentParser(description="Fix wrong things into AWS.")
    parser.add_argument("--profile", type=str, required=True, help="Profile name")
    parser.add_argument("--fix-opt", type=str, required=True, help="AWS component to fix, example: --fix tags")

    args = parser.parse_args()

    execute_command(args.profile, args.fix_opt)
