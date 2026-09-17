from unittest.mock import Mock
import pytest
from app.services import rendering


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
