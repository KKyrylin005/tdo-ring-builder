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
