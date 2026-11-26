"""The camera stops before the ring, even after changing its parts."""
import math
from conftest import open_builder, tile


CAMERA = """() => {
    const scene = window.webGiViewers[0].scene;
    const camera = scene.activeCamera;
    const bounds = scene.getModelBounds();
    const center = bounds.getCenter(camera.position.clone());
    const radius = bounds.getSize(camera.position.clone()).length() / 2;
    return {
        distance: camera.position.distanceTo(camera.controls.target),
        minimum: camera.controls.minDistance,
        safeDistance: radius + center.distanceTo(camera.controls.target) + camera.cameraObject.near,
        zoom: camera.cameraObject.zoom
    };
}"""


def zoom_to_limit(page):
    viewer = page.locator('#ring-3d')
    viewer.scroll_into_view_if_needed()
    box = viewer.bounding_box()
    page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    page.keyboard.down('Control')
    for _ in range(35):
        page.mouse.wheel(0, -2000)
        page.wait_for_timeout(80)
    page.keyboard.up('Control')
    page.wait_for_function("""() => { const c = webGiViewers[0].scene.activeCamera; return Math.abs(c.position.distanceTo(c.controls.target) - c.controls.minDistance) < 0.02; }""", timeout=10000)
    state = page.evaluate(CAMERA)
    assert state['distance'] > state['safeDistance'], state
    assert math.isclose(state['distance'], state['minimum'], rel_tol=0.02), state
    assert state['zoom'] == 1, state


def test_zoom_stops_after_model_change_and_in_fullscreen(page, base_url):
    open_builder(page, base_url)
    page.wait_for_selector('#ring-3d.ready', timeout=60000)
    zoom_to_limit(page)
    for axis, label in [('shape', 'Marquise'), ('shank', 'Double pavé')]:
        tile(page, axis, label).click()
        page.wait_for_timeout(2500)
        zoom_to_limit(page)
    page.locator('#ring-3d').get_by_role('button', name='Full screen', exact=True).click()
    page.wait_for_function("document.fullscreenElement !== null")
    zoom_to_limit(page)
    page.keyboard.press('Escape')
    assert page.errors == []

