from doculens.core import build_index, chunk_text, evaluate, search


def test_chunking_keeps_section_metadata():
    chunks = chunk_text("""# One
alpha
# Two
beta""", 'notes.md', 100)
    assert [c.section for c in chunks] == ['One', 'Two']
    assert chunks[0].start_line == 1


def test_search_returns_citation_and_abstains():
    index = build_index(chunk_text("""# Guide
Use a baseline and report uncertainty.""", 'guide.md'))
    supported = search(index, 'report uncertainty')
    assert supported['status'] == 'supported'
    assert supported['evidence'][0]['source'] == 'guide.md'
    assert search(index, 'unrelated cafeteria menu')['status'] == 'abstain'


def test_evaluation_reports_metrics():
    index = build_index(chunk_text("""# Guide
Use a baseline.""", 'guide.md'))
    report = evaluate(index, [{'query': 'use a baseline', 'relevant': ['guide-001']}])
    assert report['hit_rate'] == 1.0
    assert 0 <= report['mrr'] <= 1
