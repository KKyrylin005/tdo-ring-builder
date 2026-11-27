"""Regression tests for the bugs found and fixed on 2026-11-15 (B1-B4 in the bug report)."""
from conftest import open_builder, tile, go_to_step


# B1: ?pave= accepts any key that exists on a plain object (constructor, toString...)
def test_pave_param_rejects_prototype_keys(page, base_url):
    open_builder(page, base_url, '?pave=constructor')
    go_to_step(page, 'Band')
    tile(page, 'shank', 'Pavé').click()
    page.wait_for_function("document.querySelector('[data-axis=\"shank\"] .step-value').textContent.includes('Pav')")
    value = page.locator('[data-axis="shank"] .step-value').inner_text()
    assert 'constructor' not in value, value
    # one side stone colour is always marked as picked
    assert page.locator('.side-stones .tile[aria-pressed="true"]').count() == 1


def test_pave_param_does_not_rebuild_the_material_in_a_loop(page, base_url):
    open_builder(page, base_url, '?pave=constructor')
    page.wait_for_selector('#ring-3d.ready', timeout=60000)
    go_to_step(page, 'Band')
    tile(page, 'shank', 'Pavé').click()
    version = """() => { const vs = window.webGiViewers; const v = vs[vs.length - 1]; let m = null;
      v.scene.modelRoot.traverse(o => { if (o.isMesh && o.material && ['Gem 02', 'Gem 05'].includes(o.material.name)) m = o.material; });
      return m ? m.version : null; }"""
    page.wait_for_function(f"({version})() !== null", timeout=60000)
    page.wait_for_timeout(4000)
    v0 = page.evaluate(version)
    page.wait_for_timeout(4000)
    assert page.evaluate(version) - v0 < 3, 'side stone material keeps recompiling'


# B2: a shared link whose state no longer matches the configurator kills the whole builder
def test_broken_state_in_link_still_opens_the_builder(page, base_url):
    page.goto(base_url + '?state=garbage123')
    page.wait_for_function("document.querySelectorAll('#steps .step').length > 0 || /not available/.test(document.getElementById('status').textContent)", timeout=40000)
    assert page.locator('#steps .step').count() > 0, page.locator('#status').inner_text()


# B3: when the configurator cannot load, Back and Next stay active but do nothing
def test_failed_load_hides_dead_controls(page, base_url):
    page.goto(base_url + '?id=doesNotExist000')
    page.wait_for_function("/not available/.test(document.getElementById('status').textContent)", timeout=40000)
    assert not page.locator('#next').is_visible() or page.locator('#next').is_disabled()
    assert not page.locator('#select-ring').is_visible()
    assert 'E_' not in page.locator('#status').inner_text()


# B4 (review "Change" buttons) is gone with the one-page layout (23.11); Select this ring now sits under the choices
def test_select_ring_saves_the_choice(page, base_url):
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=60000)
    page.locator('#select-ring').click()
    page.wait_for_selector('#picked-text:not([hidden])')
    assert 'Saved' in page.locator('#picked-text').inner_text()
    assert 'state=' in page.url


# B5: the 3D area is role="img", which hides its controls (Reset view, Full screen...) from screen readers
def test_viewer_controls_are_exposed_to_assistive_tech(page, base_url):
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=60000)
    page.wait_for_function("""() => { const h = [...document.querySelectorAll('#ring-3d *')].find(e => e.shadowRoot);
        return h && h.shadowRoot.querySelector('.viewer-options button[aria-label="Reset view"]'); }""", timeout=30000)
    snap = page.locator('#ring-3d').aria_snapshot()
    assert 'Reset view' in snap, snap


def test_every_centre_stone_has_its_own_light_map(page, base_url):
    """27.11: iJewel cached one facet map for every stone named "Gem 01", so an Emerald was lit like the first
    stone (Round). Each stone geometry must carry its own map."""
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=90000)
    tile(page, 'shape', 'Emerald').click()
    page.wait_for_function("session.selection().shape === 'emerald'", timeout=20000)
    page.wait_for_timeout(6000)
    ok = page.evaluate("""(() => {
      var v = viewers3d().find(x => x && x.scene), g;
      v.scene.modelRoot.traverse(o => { if (o.isMesh && o.material && o.material.name === 'Gem 01') g = o; });
      var cache = v.getPluginByType('Diamond')._normalCapture._normalsCache;
      return !!g && g.geometry.userData.__tdoNormals === 'tdo:' + g.geometry.uuid && cache['tdo:' + g.geometry.uuid] !== cache['Gem 01'];
    })()""")
    assert ok
    assert page.errors == []
