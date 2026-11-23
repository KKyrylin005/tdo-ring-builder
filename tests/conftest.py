"""Shared fixtures: serve the repo locally and open the builder in headless Chromium.

The page loads the real iJewel SDK and configurator, so these tests need network access.
Run from the repo root: python3 -m pytest tests -q
"""
import functools, http.server, os, threading, socket
import pytest
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope='session')
def base_url():
    url = os.environ.get('TDO_BASE_URL')
    if url:
        yield url.rstrip('/') + '/'
        return
    port = _free_port()
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(_Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{port}/index.html'
    srv.shutdown()


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        yield b
        b.close()


@pytest.fixture
def page(browser):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
    pg = ctx.new_page()
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    yield pg
    ctx.close()


def open_builder(page, base_url, query='', wait_steps=True):
    page.goto(base_url + query)
    if wait_steps:
        page.wait_for_selector('#steps .step', state='attached', timeout=40000)
    return page


def tile(page, axis, label):
    return page.locator(f'#steps [data-axis="{axis}"] > .opts .tile', has_text=label).first


def go_to_step(page, title):
    # All choices sit on one page (23.11): bring the section into view instead of clicking a step
    page.locator('#steps .step-panel', has=page.locator('.step-title .name', has_text=title)).first.scroll_into_view_if_needed()


SECTIONS = ['Diamond shape', 'Diamond colour', 'Head style', 'Band', 'Metal']


def section_names(page):
    return page.locator('#steps .step-panel:not([hidden]) .step-title .name').evaluate_all('els => els.map(e => e.textContent)')
