"""Command line demo for ingredient-based recipe search."""

import argparse
from pathlib import Path

from .index import RecipeIndex
from .normalize import parse_query
from .ranker import LAMBDA, Result, search

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "sample_recipes.csv"


def format_result(rank: int, result: Result) -> str:
    lines = [
        f"{rank}. {result.name}  score={result.final_score:.2f}"
        f"  coverage={result.coverage:.2f}  {result.minutes} min",
        f"   uses:    {', '.join(result.used_ingredients)}",
    ]
    if result.missing_ingredients:
        lines.append(f"   missing: {', '.join(result.missing_ingredients)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rank recipes by the ingredients you already have."
    )
    parser.add_argument(
        "--ingredients", required=True, help="comma separated list of what is in your fridge"
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="recipe CSV to search")
    parser.add_argument("--top", type=int, default=10, help="number of recipes to show")
    parser.add_argument(
        "--max-missing", type=int, default=3, help="hide recipes needing more than this many extras"
    )
    parser.add_argument(
        "--lam", type=float, default=LAMBDA, help="weight of the missing ingredient penalty"
    )
    parser.add_argument(
        "--no-staples",
        action="store_true",
        help="count salt, oil, flour and other staples as missing",
    )
    args = parser.parse_args(argv)

    index = RecipeIndex.from_csv(args.data)
    query = parse_query(args.ingredients)
    print(f"fridge: {', '.join(query)}")

    unrecognized = [term for term in query if not index.df(term)]
    if unrecognized:
        print(f"no recipe uses: {', '.join(unrecognized)}")

    results = search(
        query,
        index,
        top_k=args.top,
        lam=args.lam,
        max_missing=args.max_missing,
        assume_staples=not args.no_staples,
    )
    if not results:
        print("Nothing matched within the missing ingredient limit.")
        return 1

    print()
    for rank, result in enumerate(results, 1):
        print(format_result(rank, result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
