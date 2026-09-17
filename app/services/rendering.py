"""Isolated, time-bounded Chromium jobs. No user content is written to permanent storage."""
import base64
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import zipfile
from flask import current_app, render_template
from app.models.designs import find_design, design_css, FONT_FILES

_slots = threading.BoundedSemaphore(2)
_pdfium_lock = threading.Lock()  # PDFium is not thread-safe.


class ExportError(Exception):
    def __init__(self, code, message='The export could not finish. Your draft is safe. Please try again.'):
        self.code, self.public_message = code, message


def worker_python():
    """Embedded WSGI runtimes may expose uWSGI itself as sys.executable."""
    configured = current_app.config.get('RENDER_PYTHON_EXECUTABLE')
    if configured:
        return configured
    candidate = Path(sys.prefix) / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    return str(candidate) if candidate.is_file() else sys.executable


def renderer_failure(stderr):
    # Never log raw browser output: it can contain document content or paths.
    detail = stderr.decode('utf-8', errors='replace').lower()
    if 'no module named' in detail:
        return 'renderer_dependency'
    if "executable doesn't exist" in detail or 'executable doesn’t exist' in detail:
        return 'browser_missing'
    if 'no usable sandbox' in detail or 'operation not permitted' in detail or 'running as root without --no-sandbox' in detail:
        return 'browser_sandbox_or_permissions'
    if 'error while loading shared libraries' in detail:
        return 'browser_system_dependency'
    return 'renderer'


def preview_document(document, thumbnail=False):
    """Rasterize the actual export, never a second HTML layout or browser screenshot.

    Results are returned to the requesting browser only. No profile/PDF cache or
    addressable preview files are kept on the server.
    """
    pdf, _, _ = export_document(document, 'pdf')
    with _pdfium_lock:
        import pypdfium2 as pdfium
        with pdfium.PdfDocument(pdf) as source:
            count = len(source)
            pages = []
            for index in range(1 if thumbnail else count):
                page = source[index]
                try:
                    width = 300 if thumbnail else 1200
                    bitmap = page.render(scale=width / page.get_width())
                    try:
                        image = bitmap.to_pil().convert('RGB')
                        try:
                            output = io.BytesIO()
                            image.save(output, format='WEBP', quality=85, method=3)
                            pages.append(base64.b64encode(output.getvalue()).decode('ascii'))
                        finally:
                            image.close()
                    finally:
                        bitmap.close()
                finally:
                    page.close()
    result = dict(pageCount=count, pages=pages, width=210, height=297)
    if not thumbnail:
        result['pdf'] = base64.b64encode(pdf).decode('ascii')
        result['accessible'] = {'name': document['name'], 'sections': document['sections']}
        # A readable text alternative for the raster pages, in the same section order.
        result['text'] = '\n'.join([document['name']] + [
            '\n'.join([section['title']] + [
                f"{row['label']}: {row['value']}"
                for group in section['groups'] for row in group
            ]) for section in document['sections']
        ])
    return result


def build_document_html(document):
    from app.services.repaired_documents import build_repaired_html
    return build_repaired_html(document)


def export_document(document, kind):
    if not _slots.acquire(blocking=False):
        raise ExportError('busy', 'Exports are busy right now. Please try again in a moment.')
    try:
        html = build_document_html(document)
        worker = Path(__file__).with_name('render_worker.py')
        job = json.dumps(dict(html=html, executable=current_app.config['CHROMIUM_EXECUTABLE']))
        try:
            process = subprocess.Popen([worker_python(), str(worker)], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       start_new_session=True)
            output, stderr = process.communicate(job.encode(), timeout=current_app.config['EXPORT_TIMEOUT_SECONDS'])
        except OSError:
            raise ExportError('renderer_worker_start') from None
        except subprocess.TimeoutExpired:
            # Terminate the browser descendants too, not just the Python wrapper.
            if os.name == 'posix':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.communicate()
            raise ExportError('timeout') from None
        if process.returncode or not output.startswith(b'%PDF'):
            raise ExportError(renderer_failure(stderr))
        pdf = output
        # Check the page limit before allocating image buffers.
        with _pdfium_lock:
            import pypdfium2 as pdfium
            with pdfium.PdfDocument(pdf) as document_pdf:
                if len(document_pdf) > 20:
                    raise ExportError('pages', 'This document is over 20 pages. Please shorten it before exporting.')
                if kind == 'pdf':
                    return pdf, 'application/pdf', 'pdf'
                images = []
                for index in range(len(document_pdf)):
                    page = document_pdf[index]
                    try:
                        bitmap = page.render(scale=1.7)
                        photo = bitmap.to_pil().convert('RGB')
                        output = io.BytesIO()
                        photo.save(output, format='PNG' if kind == 'png' else 'JPEG', **({'optimize': True} if kind == 'png' else {'quality': 88, 'optimize': True}))
                        photo.close()
                        bitmap.close()
                        images.append(output.getvalue())
                    finally:
                        page.close()
        if len(images) == 1:
            return images[0], 'image/png' if kind == 'png' else 'image/jpeg', kind
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            for index, image in enumerate(images, 1):
                bundle.writestr(f'biodata-page-{index:02d}.{kind}', image)
        return archive.getvalue(), 'application/zip', 'zip'
    finally:
        _slots.release()
