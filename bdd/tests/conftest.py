# tests/conftest.py
import os
import shutil
import pathlib
from datetime import datetime

import pytest
from dotenv import load_dotenv
from pytest_bdd import given, when, then  # noqa: F401 (activa auto-registro)

# --- Soporte multi-ambiente ---------------------------------------------------
def _load_env_file(env_name: str):
    root = pathlib.Path(__file__).resolve().parents[1]
    # tests/ -> proyecto
    candidate = root / f".env.{env_name}"
    default = root / ".env"
    if candidate.exists():
        load_dotenv(dotenv_path=candidate, override=True)
    elif default.exists():
        load_dotenv(dotenv_path=default, override=True)

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=os.getenv("TEST_ENV", "local"),
        help="Ambiente de pruebas: local|qa|uat",
    )

@pytest.fixture(scope="session", autouse=True)
def load_env(pytestconfig):
    env_name = pytestconfig.getoption("--env")
    _load_env_file(env_name)
    os.environ["TEST_ENV"] = env_name
    print(f"🌎 Ambiente cargado: {env_name}")

# --- Parámetros base ----------------------------------------------------------
@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL", "http://localhost:5173")
    return url.rstrip("/")

@pytest.fixture(scope="session")
def api_base_url():
    url = os.getenv("API_BASE_URL", "http://localhost:8000")
    return url.rstrip("/")

@pytest.fixture(scope="session")
def run_headless():
    return os.getenv("PW_HEADLESS", "1") == "1"

@pytest.fixture(scope="session")
def pw_browser_name():
    return os.getenv("PW_BROWSER", "chromium")

@pytest.fixture(scope="session")
def pw_trace_mode():
    # off | on | retain-on-failure
    return os.getenv("PW_TRACE", "on")

# --- Playwright: browser/context/page ----------------------------------------
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance, pw_browser_name, run_headless):
    browser = getattr(playwright_instance, pw_browser_name).launch(
        headless=run_headless,
        args=["--start-maximized"]
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser, pw_trace_mode, tmp_path_factory):
    # carpeta para artifacts por test
    artifacts_dir = tmp_path_factory.mktemp("artifacts")
    ctx = browser.new_context(record_video_dir=str(artifacts_dir / "video"))
    # tracing
    if pw_trace_mode in ("on", "retain-on-failure"):
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx

    # el cierre/stop tracing lo manejamos en hook del escenario para decidir guardar o no
    ctx.close()

@pytest.fixture(scope="function")
def page(context, base_url):
    page = context.new_page()
    page.set_default_timeout(10_000)
    # si tu flujo siempre inicia en UI:
    page.goto(base_url)
    return page

# --- API request context (para pruebas de API/TDD de backend) ----------------
@pytest.fixture(scope="function")
def api(playwright_instance, api_base_url):
    request_context = playwright_instance.request.new_context(
        base_url=api_base_url,
        extra_http_headers={"Accept": "application/json"}
    )
    yield request_context
    request_context.dispose()

# --- Hooks BDD / Artifacts por escenario -------------------------------------
def _ensure_dir(path: pathlib.Path):
    path.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_bdd_before_scenario(request, feature, scenario):
    # Crea carpeta por escenario
    feature_name = pathlib.Path(feature.filename).stem
    scenario_name = scenario.name.replace(" ", "_").replace("/", "_")
    outdir = pathlib.Path("test-results") / feature_name / f"{scenario_name}_{_now()}"
    _ensure_dir(outdir)
    request.node._bdd_outdir = outdir
    yield

@pytest.hookimpl(hookwrapper=True)
def pytest_bdd_after_scenario(request, feature, scenario):
    outcome = yield
    failed = outcome.excinfo is not None
    outdir: pathlib.Path = getattr(request.node, "_bdd_outdir", pathlib.Path("test-results") / "unknown")

    # Guardar TRACE y Screenshot final si falló
    # Tomamos page/context de fixtures si existen:
    page = request.node.funcargs.get("page")
    context = request.node.funcargs.get("context")

    if context:
        try:
            trace_path = outdir / "trace.zip"
            # Si falló siempre guardamos, si no, solo si PW_TRACE = on
            trace_mode = os.getenv("PW_TRACE", "on")
            if failed or trace_mode == "on":
                context.tracing.stop(path=str(trace_path))
        except Exception:
            pass

    if failed and page:
        try:
            page.screenshot(path=str(outdir / "failed.png"), full_page=True)
        except Exception:
            pass

    print(f"📦 Artifacts: {outdir} | ❌ Failed: {failed}")

# --- Marcadores cómodos -------------------------------------------------------
def pytest_configure(config):
    config.addinivalue_line("markers", "ui: pruebas UI con Playwright")
    config.addinivalue_line("markers", "api: pruebas API con Playwright request context")
    config.addinivalue_line("markers", "smoke: subset rápido")
    config.addinivalue_line("markers", "slow: pruebas lentas")
