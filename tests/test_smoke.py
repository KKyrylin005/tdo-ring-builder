from conftest import open_builder, tile, go_to_step


def test_builder_loads_and_has_steps(page, base_url):
    open_builder(page, base_url)
    names = page.locator('.seg').evaluate_all('els => els.map(e => e.title)')
    assert names == ['Diamond shape', 'Diamond colour', 'Band', 'Prongs', 'Metal', 'Review']
    assert page.errors == []
