"""Phone layout and fast clicking."""
from conftest import open_builder, tile, go_to_step
import pytest


@pytest.mark.parametrize('w', [320, 375, 390])
def test_no_horizontal_overflow_on_phones(browser, base_url, w):
    ctx = browser.new_context(viewport={'width': w, 'height': 760}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    open_builder(pg, base_url)
    for t in ['Diamond shape', 'Carat', 'Diamond colour', 'Band', 'Prongs', 'Metal', 'Review']:
        go_to_step(pg, t)
        if t == 'Band':
            tile(pg, 'shank', 'Pavé').click(); pg.wait_for_timeout(800)
        sw = pg.evaluate('document.documentElement.scrollWidth'); cw = pg.evaluate('document.documentElement.clientWidth')
        assert sw <= cw, f'{t}: page {sw}px wider than screen {cw}px'
        # tiles of the visible panel stay inside the panel
        over = pg.evaluate("""() => { const p = [...document.querySelectorAll('.step-panel')].find(x => !x.hidden); const r = p.getBoundingClientRect();
            return [...p.querySelectorAll('.tile, .review-row')].filter(t => t.offsetParent && t.getBoundingClientRect().right > r.right + 1).map(t => t.textContent.trim()); }""")
        assert over == [], f'{t}: {over}'
    ctx.close()


def test_next_on_phone_keeps_the_new_step_title_in_view(browser, base_url):
    ctx = browser.new_context(viewport={'width': 390, 'height': 760}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    open_builder(pg, base_url)
    pg.wait_for_selector('#ring-3d.ready', timeout=90000)
    go_to_step(pg, 'Band')
    tile(pg, 'shank', 'Pavé').click(); pg.wait_for_timeout(800)
    pg.locator('#next').scroll_into_view_if_needed()
    pg.locator('#next').click(); pg.wait_for_function('() => new Promise(r => { let y = scrollY, n = 0; const t = setInterval(() => { if (scrollY === y && ++n > 5) { clearInterval(t); r(true); } else if (scrollY !== y) { y = scrollY; n = 0; } }, 50); })', timeout=5000)
    res = pg.evaluate("""() => { const p = [...document.querySelectorAll('.step-panel')].find(x => !x.hidden);
        const t = p.querySelector('.step-title').getBoundingClientRect(); const s = document.querySelector('.stage').getBoundingClientRect();
        return {titleTop: t.top, titleBottom: t.bottom, stageBottom: s.bottom, vh: innerHeight}; }""")
    assert res['titleTop'] >= res['stageBottom'] - 1 and res['titleBottom'] <= res['vh'], res
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
