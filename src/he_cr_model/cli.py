from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .data_loader import load_reaction_records
from .levels import LEVELS_N5
from .reactions import load_reactions
from .reaction_network_builder import build_network_from_table_i_reference, export_network_build_result
from .solver import fail_closed_scan_message
from .spectra import load_spectral_lines, missing_verified_transition_data
from .validation import validate_reaction_records


def cmd_list_levels(_: argparse.Namespace) -> int:
    print("level_id,n,spin,orbital,label,review_status")
    for level in LEVELS_N5:
        print(f"{level.level_id},{level.n},{level.spin_multiplicity},{level.orbital},{level.label},{level.review_status}")
    return 0


def cmd_list_reactions(args: argparse.Namespace) -> int:
    reactions = load_reactions()
    print("reaction_id,process,unit,review_status,enabled_by_default,source")
    for reaction in reactions:
        if not args.all and not reaction.is_enabled:
            continue
        print(
            f"{reaction.reaction_id},{reaction.process},{reaction.unit},"
            f"{reaction.review_status},{str(reaction.enabled_by_default).lower()},{reaction.source}"
        )
    return 0


def cmd_audit_data(_: argparse.Namespace) -> int:
    issues = validate_reaction_records(load_reaction_records())
    if not issues:
        print("data audit passed")
        return 0
    print("severity,item_id,message")
    for issue in issues:
        print(f"{issue.severity},{issue.item_id},{issue.message}")
    return 1 if any(issue.severity == "error" for issue in issues) else 0


def cmd_spectrum(_: argparse.Namespace) -> int:
    lines = load_spectral_lines()
    print("line_id,wavelength_nm,transition,review_status,enabled_by_default")
    for line in lines:
        print(
            f"{line.line_id},{line.wavelength_nm},{line.transition},"
            f"{line.review_status},{str(line.enabled_by_default).lower()}"
        )
    missing = missing_verified_transition_data(lines)
    if missing:
        print("missing_verified_transition_data=" + ";".join(missing), file=sys.stderr)
        return 2
    return 0


def cmd_scan(_: argparse.Namespace) -> int:
    print(fail_closed_scan_message(), file=sys.stderr)
    return 2


def cmd_build_network(args: argparse.Namespace) -> int:
    output_path = Path(args.output)
    result = build_network_from_table_i_reference()
    export_network_build_result(output_path, result)
    print(
        "network_build_exported "
        f"output={output_path} "
        f"templates={len(result.templates)} "
        f"network_all={len(result.network_all)} "
        f"network_solver_ready={len(result.network_solver_ready)} "
        f"issues={len(result.validation_issues)}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="he-cr")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_levels = subparsers.add_parser("list-levels")
    list_levels.set_defaults(func=cmd_list_levels)

    list_reactions = subparsers.add_parser("list-reactions")
    list_reactions.add_argument("--all", action="store_true", help="include disabled reactions")
    list_reactions.set_defaults(func=cmd_list_reactions)

    audit_data = subparsers.add_parser("audit-data")
    audit_data.set_defaults(func=cmd_audit_data)

    spectrum = subparsers.add_parser("spectrum")
    spectrum.set_defaults(func=cmd_spectrum)

    scan = subparsers.add_parser("scan")
    scan.set_defaults(func=cmd_scan)

    build_network = subparsers.add_parser("build-network")
    build_network.add_argument(
        "--output",
        default=str(Path("data") / "staged" / "network_build.json"),
        help="path to exported network build audit json",
    )
    build_network.set_defaults(func=cmd_build_network)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
