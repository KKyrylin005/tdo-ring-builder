"""Phone layout and fast clicking."""
from conftest import open_builder, tile, go_to_step, SECTIONS
import pytest


def test_mobile_menu_exposes_all_navigation_links(browser, base_url):
    with browser.new_context(viewport={'width': 320, 'height': 568}, is_mobile=True, has_touch=True) as ctx:
        pg = ctx.new_page()
        open_builder(pg, base_url, wait_steps=False)
        menu = pg.get_by_role('button', name='Menu', exact=True)
        design = pg.locator('#main-menu .studio')
        assert pg.evaluate('window.scrollY') == 0
        assert not design.is_visible()
        menu.tap()
        assert menu.get_attribute('aria-expanded') == 'true'
        assert design.is_visible()
        design.focus()
        pg.keyboard.press('Escape')
        assert menu.get_attribute('aria-expanded') == 'false'
        assert menu.evaluate('el => document.activeElement === el')


@pytest.mark.parametrize('w', [320, 375, 390])
def test_no_horizontal_overflow_on_phones(browser, base_url, w):
    ctx = browser.new_context(viewport={'width': w, 'height': 760}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    open_builder(pg, base_url)
    go_to_step(pg, 'Band')
    tile(pg, 'shank', 'Pavé').click(); pg.wait_for_timeout(800)
    sw = pg.evaluate('document.documentElement.scrollWidth'); cw = pg.evaluate('document.documentElement.clientWidth')
    assert sw <= cw, f'page {sw}px wider than screen {cw}px'
    # tiles of every section stay inside their section
    over = pg.evaluate("""() => [...document.querySelectorAll('.step-panel:not([hidden])')].flatMap(p => { const r = p.getBoundingClientRect();
        return [...p.querySelectorAll('.tile')].filter(t => t.offsetParent && t.getBoundingClientRect().right > r.right + 1).map(t => t.textContent.trim()); })""")
    assert over == [], over
    ctx.close()


def test_phone_shows_every_section_under_the_ring(browser, base_url):
    """One page on a phone too: all sections are there, one under another, below the 3D view."""
    ctx = browser.new_context(viewport={'width': 390, 'height': 760}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    open_builder(pg, base_url)
    tops = pg.evaluate("""() => [...document.querySelectorAll('.step-panel:not([hidden])')].map(p => p.getBoundingClientRect().top + scrollY)""")
    stage = pg.evaluate("() => document.querySelector('.stage').getBoundingClientRect().bottom + scrollY")
    assert len(tops) == len(SECTIONS) and tops == sorted(tops) and tops[0] >= stage - 1, (tops, stage)
    ctx.close()


def test_fast_band_switch_leaves_ui_in_step_with_selection(page, base_url):
    open_builder(page, base_url)
    go_to_step(page, 'Band')
    tile(page, 'shank', 'Pavé').click()
    tile(page, 'shank', 'Solitaire').click()
    tile(page, 'shank', 'Pavé').click()
    tile(page, 'shank', 'Solitaire').click()
    page.wait_for_timeout(2500)
    pressed = page.locator('[data-axis="shank"] > .opts .tile[aria-pressed="true"]').inner_text()
    side_open = page.locator('.side-stones').evaluate('e => e.classList.contains("open")')
    assert pressed == 'Solitaire' and not side_open, (pressed, side_open)
