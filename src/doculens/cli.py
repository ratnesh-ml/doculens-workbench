import argparse
import json
from pathlib import Path

from .core import build_index, evaluate, load_documents, load_index, save_index, search


def main(argv=None):
    parser = argparse.ArgumentParser(prog='doculens')
    sub = parser.add_subparsers(dest='command', required=True)
    ingest = sub.add_parser('ingest')
    ingest.add_argument('folder')
    ingest.add_argument('--index', default='.doculens/index.json')
    find = sub.add_parser('search')
    find.add_argument('query')
    find.add_argument('--index', default='.doculens/index.json')
    find.add_argument('--top-k', type=int, default=5)
    ev = sub.add_parser('evaluate')
    ev.add_argument('questions')
    ev.add_argument('--index', default='.doculens/index.json')
    args = parser.parse_args(argv)

    if args.command == 'ingest':
        index = build_index(load_documents(args.folder))
        save_index(index, args.index)
        print(json.dumps({'chunks': len(index.chunks), 'index': args.index}, indent=2))
        return 0
    index = load_index(args.index)
    if args.command == 'search':
        print(json.dumps(search(index, args.query, args.top_k), indent=2))
        return 0
    records = [json.loads(line) for line in Path(args.questions).read_text(encoding='utf-8').splitlines() if line.strip()]
    print(json.dumps(evaluate(index, records), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
