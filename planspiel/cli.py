import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="planspiel",
        description="Werkzeuge für das CIA-Planspiel (Simulation, Prüfungen).",
    )
    parser.add_subparsers(dest="command")
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
    return 0
