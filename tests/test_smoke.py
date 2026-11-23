from conftest import open_builder, tile, go_to_step


def test_builder_loads_and_has_steps(page, base_url):
    open_builder(page, base_url)
    names = page.locator('.seg').evaluate_all('els => els.map(e => e.title)')
    assert names == ['Diamond shape', 'Diamond colour', 'Head style', 'Band', 'Metal', 'Review']
    assert page.errors == []


SHAPES = ['Round', 'Oval', 'Pear', 'Cushion', 'Emerald', 'Marquise', 'Heart', 'Radiant', 'Princess', 'Asscher', 'Elongated Cushion']


def test_one_carat_and_all_shapes(page, base_url):
    """Every ring is shown at 2 ct (23.11): no Carat step, the 2.00 ct shows next to the shape,
    the 11 shapes of the requirements are there and each has its own icon."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    go_to_step(page, 'Diamond shape')
    tiles = page.locator('#steps [data-axis="shape"] > .opts .tile')
    labels = tiles.evaluate_all('els => els.map(e => e.innerText.trim())')
    assert labels == SHAPES, labels
    icons = tiles.evaluate_all('els => els.map(e => e.querySelector("svg").innerHTML)')
    assert len(set(icons)) == len(icons), 'every shape needs its own icon'
    assert page.locator('[data-axis="carat"]').count() == 0
    assert '2.00 ct' in page.locator('[data-axis="shape"] .step-value').inner_text()
    assert page.errors == []


NEW_BANDS = ['Solitaire', 'Pavé', 'Twisted', 'Marquise & round', 'Double pavé', 'Flush accent', 'Side stone', 'Ribbed side stone']


def test_bands_have_icons_and_side_stones(page, base_url):
    """Chiraj's 8 bands from 18.11, named as in the requirements: each band a shopper can pick has its own icon,
    and bands with stones open the side stones colour."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    go_to_step(page, 'Band')
    tiles = page.locator('#steps [data-axis="shank"] > .opts .tile')
    labels = tiles.evaluate_all('els => els.map(e => e.innerText.trim())')
    for b in NEW_BANDS:
        assert b in labels, labels
    icons = tiles.evaluate_all('els => els.filter(e => !e.disabled && e.getAttribute("aria-disabled") !== "true").map(e => e.querySelector("svg").innerHTML)')
    assert len(set(icons)) == len(icons), 'every band a shopper can pick needs its own icon'
    side = page.locator('#steps .side-stones')
    page.locator('#steps [data-axis="shank"] > .opts .tile', has_text='Solitaire').first.click()
    page.wait_for_function("document.querySelector('[data-axis=\"shank\"] .step-value').textContent.startsWith('Solitaire')")
    assert 'open' not in side.get_attribute('class')
    page.locator('#steps [data-axis="shank"] > .opts .tile', has_text='Ribbed side stone').first.click()
    page.wait_for_function("document.querySelector('.side-stones').classList.contains('open')")
    assert page.errors == []
