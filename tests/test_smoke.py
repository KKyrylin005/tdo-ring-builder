from conftest import open_builder, tile, go_to_step, section_names, SECTIONS


def test_builder_shows_every_choice_on_one_page(page, base_url):
    """Alina, 23.11: every setting on one page, no steps, no Back and Next."""
    open_builder(page, base_url)
    assert section_names(page) == SECTIONS
    assert not page.locator('#next').is_visible() and not page.locator('#back').is_visible()
    assert not page.locator('#progress').is_visible()
    assert page.locator('#select-ring').is_visible()
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


def test_six_prong_shows_only_shapes_it_has(page, base_url):
    """26.11: 6 Prong exists for Round only. While it is picked, the other shapes fold away (not dashed tiles
    that would switch the head back), and they come back with 4 Prong."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    tile(page, 'head', '6 Prong').click()
    page.wait_for_function('document.querySelectorAll(\'#steps [data-axis="shape"] .tile.gone\').length > 0', timeout=20000)
    page.wait_for_timeout(800)
    visible = page.locator('#steps [data-axis="shape"] > .opts .tile:not(.gone)').evaluate_all('els => els.map(e => e.innerText.trim())')
    assert visible == ['Round'], visible
    tile(page, 'head', '4 Prong').click()
    page.wait_for_function('document.querySelectorAll(\'#steps [data-axis="shape"] .tile.gone\').length === 0', timeout=20000)
    assert page.locator('#steps [data-axis="shape"] > .opts .tile:not(.gone)').count() == len(SHAPES)
    assert page.errors == []


def test_section_bar_jumps_and_follows_scroll(page, base_url):
    """27.11: a bar over the choices names each section with its pick; a tap glides to the section,
    and the active tab follows the scroll."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    names = page.locator('#secnav .n').all_inner_texts()
    assert names == ['Shape', 'Colour', 'Head', 'Band', 'Metal'], names
    assert 'Round' in page.locator('#secnav [data-sec="shape"] .v').inner_text()
    page.locator('#secnav [data-sec="shank"]').click()
    page.wait_for_timeout(1500)
    assert page.locator('#secnav [aria-current="true"]').get_attribute('data-sec') == 'shank'
    band_top = page.locator('#steps .step-panel[data-axis="shank"]').evaluate('e => e.getBoundingClientRect().top')
    bar_bottom = page.locator('#secnav').evaluate('e => e.getBoundingClientRect().bottom')
    assert 0 <= band_top - bar_bottom <= 40, (band_top, bar_bottom)
    page.evaluate("document.querySelector('#steps .step-panel[data-axis=\"shape\"]').scrollIntoView()")
    page.wait_for_timeout(1200)
    assert page.locator('#secnav [aria-current="true"]').get_attribute('data-sec') == 'shape'
    assert page.errors == []
