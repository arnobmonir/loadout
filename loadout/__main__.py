"""CLI entry point."""

from __future__ import annotations

import argparse
import sys

from loadout import __version__
from loadout.cheats_cmd import scaffold_user_cheat
from loadout.config import LoadoutConfig, get_builtin_cheats_dir
from loadout.loader import CheatLoadError, find_duplicate_tools, load_cheat_file, load_cheats
from loadout.output import doctor_report
from loadout.tui import run_tui
from loadout.variables import VariableStore


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loadout",
        description="Persistent pentest command launcher",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--tag", help="Filter cheats by tag")
    parser.add_argument("--tool", help="Filter cheats by tool name")
    parser.add_argument("--study", action="store_true", help="Study mode (hints only)")

    sub = parser.add_subparsers(dest="command")

    vars_parser = sub.add_parser("vars", help="Manage global variables")
    vars_sub = vars_parser.add_subparsers(dest="vars_command", required=True)

    vars_set = vars_sub.add_parser("set", help="Set a variable (key=value)")
    vars_set.add_argument("assignment", help="e.g. ip=10.10.10.5")

    vars_sub.add_parser("list", help="List all variables")
    vars_unset = vars_sub.add_parser("unset", help="Remove a variable")
    vars_unset.add_argument("key")

    cheats_parser = sub.add_parser("cheats", help="Cheat pack utilities")
    cheats_sub = cheats_parser.add_subparsers(dest="cheats_command")

    cheats_list = cheats_sub.add_parser("list", help="List loaded cheats")
    cheats_list.add_argument(
        "--source",
        choices=["builtin", "user", "all"],
        default="all",
        help="Which cheat paths to list (default: all)",
    )

    validate = cheats_sub.add_parser("validate", help="Validate cheat YAML file(s)")
    validate.add_argument("path", nargs="?", help="File or directory to validate")
    validate.add_argument(
        "--all",
        action="store_true",
        help="Validate entire built-in cheat pack",
    )

    cheats_add = cheats_sub.add_parser("add", help="Scaffold a new user cheat file")
    cheats_add.add_argument("tool", help="Tool name (becomes tool field and filename)")

    sub.add_parser("config", help="Show configuration")
    sub.add_parser("doctor", help="Check environment readiness")
    sub.add_parser("reload", help="Reload cheats (no-op outside TUI for now)")

    return parser


def _cmd_vars(config: LoadoutConfig, args: argparse.Namespace) -> int:
    store = VariableStore(defaults=config.default_vars)
    if args.vars_command == "set":
        if "=" not in args.assignment:
            print("loadout: expected key=value", file=sys.stderr)
            return 1
        key, _, value = args.assignment.partition("=")
        key = key.strip()
        if not key:
            print("loadout: empty variable name", file=sys.stderr)
            return 1
        store.set(key, value.strip())
        print(f"Set {key}={value.strip()}")
        return 0

    if args.vars_command == "list":
        for key, value in sorted(store.list_all().items()):
            print(f"{key}={value}")
        return 0

    if args.vars_command == "unset":
        if store.unset(args.key):
            print(f"Unset {args.key}")
            return 0
        print(f"loadout: variable not set: {args.key}", file=sys.stderr)
        return 1

    return 1


def _cheat_paths_for_source(config: LoadoutConfig, source: str) -> list:
    from pathlib import Path

    if source == "builtin":
        return [get_builtin_cheats_dir()]
    if source == "user":
        return list(config.cheat_paths)
    return config.all_cheat_paths()


def _cmd_cheats(config: LoadoutConfig, args: argparse.Namespace) -> int:
    if args.cheats_command == "list":
        paths = _cheat_paths_for_source(config, args.source)
        actions = load_cheats(paths)
        for action in actions:
            print(f"{action.tool}\t{action.title}\t{action.source_file}")
        return 0

    if args.cheats_command == "validate":
        from pathlib import Path

        if args.all:
            target = get_builtin_cheats_dir()
            paths = sorted(target.rglob("*.yaml"))
            dupes = find_duplicate_tools([target])
            if dupes:
                print(
                    f"loadout: duplicate tool names in builtin pack: {', '.join(dupes)}",
                    file=sys.stderr,
                )
                return 1
        elif args.path:
            target = Path(args.path)
            if target.is_file():
                paths = [target]
            elif target.is_dir():
                paths = sorted(target.rglob("*.yaml"))
            else:
                print(f"loadout: not found: {target}", file=sys.stderr)
                return 1
        else:
            target = get_builtin_cheats_dir()
            paths = sorted(target.rglob("*.yaml"))

        errors = 0
        for path in paths:
            if path.name in {"manifest.yaml", "_template.yaml"}:
                continue
            try:
                load_cheat_file(path)
                print(f"OK  {path}")
            except CheatLoadError as exc:
                print(f"ERR {exc}", file=sys.stderr)
                errors += 1
        return 1 if errors else 0

    if args.cheats_command == "add":
        try:
            path = scaffold_user_cheat(args.tool)
        except (ValueError, FileExistsError) as exc:
            print(f"loadout: {exc}", file=sys.stderr)
            return 1
        print(f"Created {path}")
        print("Edit the file, then run: loadout cheats validate", path)
        return 0

    print("loadout: cheats subcommand required", file=sys.stderr)
    return 1


def _cmd_config(config: LoadoutConfig) -> int:
    print(f"output_mode={config.output_mode.value}")
    print(f"config_dir={config.cheat_paths[0].parent}")
    for path in config.cheat_paths:
        print(f"cheat_path={path}")
    for key, value in sorted(config.default_vars.items()):
        print(f"default.{key}={value}")
    return 0


def _cmd_doctor() -> int:
    failed = False
    for check, status, detail in doctor_report():
        print(f"[{status.upper():4}] {check}: {detail}")
        if status == "fail":
            failed = True
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        config = LoadoutConfig.load()
        config.ensure_dirs()
    except Exception as exc:
        print(f"loadout: config error: {exc}", file=sys.stderr)
        return 2

    if args.command == "vars":
        return _cmd_vars(config, args)
    if args.command == "cheats":
        return _cmd_cheats(config, args)
    if args.command == "config":
        return _cmd_config(config)
    if args.command == "doctor":
        return _cmd_doctor()
    if args.command == "reload":
        print("Reload is automatic inside the TUI (type reload).")
        return 0

    var_store = VariableStore(defaults=config.default_vars)
    try:
        run_tui(config, var_store, tag=args.tag, tool=args.tool, study=args.study)
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"loadout: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
