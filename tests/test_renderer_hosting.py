from unittest.mock import Mock
import pytest
from app.services import rendering
from app.services.render_worker import launch_options
import json
import os


def test_worker_uses_virtualenv_in_embedded_server(app, monkeypatch, tmp_path):
    interpreter = tmp_path / 'bin' / 'python'
    interpreter.parent.mkdir()
    interpreter.touch()
    monkeypatch.setattr(rendering.sys, 'prefix', str(tmp_path))
    monkeypatch.setattr(rendering.sys, 'executable', '/usr/bin/uwsgi')
    with app.app_context():
        assert rendering.worker_python() == str(interpreter)
        app.config['RENDER_PYTHON_EXECUTABLE'] = '/custom/venv/bin/python'
        assert rendering.worker_python() == '/custom/venv/bin/python'


@pytest.mark.parametrize('stderr,code', [
    (b"Executable doesn't exist at /private/path", 'browser_missing'),
    (b'No usable sandbox!', 'browser_sandbox_or_permissions'),
    (b"No module named 'playwright'", 'renderer_dependency'),
    (b'error while loading shared libraries: libX.so', 'browser_system_dependency'),
    (b'Unknown failure with private document contents', 'renderer'),
])
def test_worker_failure_is_classified_without_exposing_content(app, monkeypatch, stderr, code):
    monkeypatch.setattr(rendering, 'build_document_html', lambda doc: '<p>Private</p>')
    process = Mock(returncode=1)
    process.communicate.return_value = (b'', stderr)
    monkeypatch.setattr(rendering.subprocess, 'Popen', Mock(return_value=process))
    with app.app_context(), pytest.raises(rendering.ExportError) as caught:
        rendering.export_document({}, 'pdf')
    assert caught.value.code == code
    assert 'private' not in caught.value.public_message.lower()


def test_missing_worker_is_recoverable(app, monkeypatch):
    monkeypatch.setattr(rendering, 'build_document_html', lambda doc: '')
    monkeypatch.setattr(rendering.subprocess, 'Popen', Mock(side_effect=FileNotFoundError))
    with app.app_context(), pytest.raises(rendering.ExportError) as caught:
        rendering.export_document({}, 'pdf')
    assert caught.value.code == 'renderer_worker_start'


@pytest.mark.parametrize('job,enabled', [
    ({}, True), ({'sandbox': True}, True), ({'sandbox': False}, False),
    ({'sandbox': 'false'}, True), ({'sandbox': None}, True),
])
def test_browser_sandbox_requires_explicit_boolean_opt_out(job, enabled):
    assert launch_options(job)['chromium_sandbox'] is enabled


@pytest.mark.parametrize('enabled', [True, False])
def test_sandbox_policy_comes_from_server_not_document(app, monkeypatch, enabled):
    monkeypatch.setattr(rendering, 'build_document_html', lambda doc: '<p>Sample</p>')
    process = Mock(returncode=1)
    process.communicate.return_value = (b'', b'No usable sandbox!')
    start = Mock(return_value=process)
    monkeypatch.setattr(rendering.subprocess, 'Popen', start)
    with app.app_context():
        app.config['CHROMIUM_SANDBOX'] = enabled
        with pytest.raises(rendering.ExportError):
            rendering.export_document({'sandbox': not enabled}, 'pdf')
    job = json.loads(process.communicate.call_args.args[0])
    assert job['sandbox'] is enabled
    assert start.call_count == 1  # No automatic insecure fallback.


@pytest.mark.skipif(os.getenv('RUN_EXPORT_TESTS') != '1', reason='Real Chromium preview')
def test_preview_with_explicit_host_sandbox_opt_out(app):
    from app.models.catalog import demo_profile
    from app.models.profile import Profile
    with app.app_context():
        app.config['CHROMIUM_SANDBOX'] = False
        result = rendering.preview_document(Profile.parse(demo_profile()).document())
    assert result['pageCount'] >= 1
    assert len(result['pages']) == result['pageCount']
    assert result['pdf'].startswith('JVBER')
