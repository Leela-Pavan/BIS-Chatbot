from app.knowledge.extractors import extract_html


def test_html_extraction_preserves_page_and_clause_context() -> None:
    document = extract_html(
        b"<html><body><h1>DEMO DATA - NOT OFFICIAL</h1>"
        b"<p>1 Scope</p><p>Applies to the synthetic fixture.</p>"
        b"<script>ignore this</script><p>2 Requirements</p><p>Use evidence.</p>"
        b"</body></html>"
    )

    assert len(document.pages) == 1
    assert "ignore this" not in document.pages[0].text
    assert [clause.clause_number for clause in document.clauses] == ["1", "2"]
    assert document.clauses[0].page_number == 1
    assert "synthetic fixture" in document.clauses[0].text
