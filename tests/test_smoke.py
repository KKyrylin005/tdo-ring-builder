from conftest import open_builder, tile, go_to_step


def test_builder_loads_and_has_steps(page, base_url):
    open_builder(page, base_url)
    names = page.locator('.seg').evaluate_all('els => els.map(e => e.title)')
    assert names == ['Diamond shape', 'Carat', 'Diamond colour', 'Band', 'Prongs', 'Metal', 'Review']
    assert page.errors == []


def test_carat_switch_keeps_the_other_choices(page, base_url):
    """Each carat is its own iJewel configurator; switching carries the shape over and loads that carat's head."""
    glbs = []
    page.on('request', lambda r: glbs.append(r.url) if '.glb' in r.url else None)
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    go_to_step(page, 'Diamond shape')
    tile(page, 'shape', 'Oval').click()
    page.wait_for_function("document.querySelector('[data-axis=\"shape\"] .step-value').textContent.startsWith('Oval')")
    go_to_step(page, 'Carat')
    tile(page, 'carat', '3.00 ct').click()
    # The other carats are built in the background; the switch swaps finished 3D views
    page.wait_for_function("document.getElementById('ring-3d').dataset.shown === '3.00 ct' && document.querySelectorAll('#ring-3d .ijewel-view:not(.incoming)').length === 1 && [...document.querySelectorAll('#ring-3d .ijewel-view')].every(e => !e.style.zIndex)", timeout=120000)
    page.wait_for_timeout(1500)
    assert page.locator('#ring-3d .ijewel-view:not(.incoming)').count() == 1
    assert page.locator('[data-axis="carat"] .tile[aria-pressed="true"]').inner_text() == '3.00 ct'
    page.wait_for_timeout(2000)
    assert page.locator('[data-axis="shape"] .step-value').inner_text().startswith('Oval')
    assert any('hd01_ov_3' in u for u in glbs), glbs
    assert 'ct%3D3' in page.locator('#wa-btn').get_attribute('href')
    assert page.evaluate('window.webGiViewers.length') <= 3
    assert page.errors == []


NEW_BANDS = ['Classic', 'Petite Pavé', 'Vintage Bezel', 'Twisted Pavé', 'Split Pavé', 'Flush Accent', 'Side Stone', 'Vintage Side Stone']


def test_new_bands_have_icons_and_side_stones(page, base_url):
    """Chiraj's 8 bands from 18.11: each has its own icon; bands with stones open the side stones colour."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    go_to_step(page, 'Band')
    labels = page.locator('#steps [data-axis="shank"] > .opts .tile').evaluate_all('els => els.map(e => e.innerText.trim())')
    for b in NEW_BANDS:
        assert b in labels, labels
    icons = page.locator('#steps [data-axis="shank"] > .opts .tile svg').evaluate_all('els => els.map(e => e.innerHTML)')
    assert len(set(icons)) == len(icons), 'every band needs its own icon'
    side = page.locator('#steps .side-stones')
    page.locator('#steps [data-axis="shank"] > .opts .tile', has_text='Classic').first.click()
    page.wait_for_function("document.querySelector('[data-axis=\"shank\"] .step-value').textContent.startsWith('Classic')")
    assert 'open' not in side.get_attribute('class')
    page.locator('#steps [data-axis="shank"] > .opts .tile', has_text='Vintage Side Stone').first.click()
    page.wait_for_function("document.querySelector('.side-stones').classList.contains('open')")
    assert page.errors == []
