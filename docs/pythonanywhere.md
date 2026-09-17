# PythonAnywhere setup

The application uses a Flask factory. Do not import `app` or `run` from the
`app` package. The repository's `wsgi.py` exposes `application` and loads the
project's `.env` before configuration is imported.

## Install in the web application's virtualenv

In a PythonAnywhere Bash console:

```sh
cd /home/priyankjam/Parichay
workon myenv
python -m pip install -r requirements.txt
```

Set the Web tab's virtualenv to `/home/priyankjam/.virtualenvs/myenv`. Its
Python version must match the web application's version (3.10 in the supplied
logs). `Flask-Limiter` is already in requirements; the missing `flask_limiter`
error means it was not installed in the environment used by the web app.

## Production environment

Create or edit `/home/priyankjam/Parichay/.env` on PythonAnywhere (not the Mac's
development file):

```dotenv
APP_ENV=production
SECRET_KEY=replace-with-a-new-random-secret
TRUSTED_HOSTS=priyankjam.pythonanywhere.com
CHROMIUM_EXECUTABLE=/usr/bin/chromium
RENDER_PYTHON_EXECUTABLE=/home/priyankjam/.virtualenvs/myenv/bin/python
EXPORT_TIMEOUT_SECONDS=40
RATELIMIT_STORAGE_URI=memory://
```

Generate the secret in the console with
`python -c "import secrets; print(secrets.token_hex(32))"` and replace the
placeholder. Keep it private and stable across reloads. Never commit `.env`.
For additional domains, add their exact hostnames separated by commas, without
`https://` or paths. Use a shared limiter store before adding multiple workers.

## WSGI configuration

Replace the starter contents of
`/var/www/priyankjam_pythonanywhere_com_wsgi.py` (Web tab → WSGI configuration)
with:

```python
import sys

project = '/home/priyankjam/Parichay'
if project not in sys.path:
    sys.path.insert(0, project)

from wsgi import application
```

Enable HTTPS / Force HTTPS for the web app and click **Reload**. Do not run
`app.run()` or start the development server in the WSGI file. Test `/` and
`/create` over HTTPS. Reload after changing `.env` because configuration is
read when the application starts.

## Preview and export are a separate hosting compatibility check

The errors supplied occur before rendering. Fixing startup does not prove PDF,
PNG or live preview compatibility. These features run Chromium in an isolated
subprocess. PythonAnywhere documents using its preinstalled `/usr/bin/chromium`
instead of `playwright install`, and its example uses `--no-sandbox`.

Parichay currently requires Chromium sandboxing for user-supplied documents.
Setting the executable path alone may therefore not make rendering work on
PythonAnywhere. Confirm sandbox support with the host; if unsupported, run the
app on a host supporting sandboxed Chromium or design an isolated rendering
service before launching. The startup fix intentionally does not disable this
security boundary. The worker uses the explicit virtualenv interpreter above,
avoiding the embedded uWSGI executable. Renderer errors are logged as safe
categories such as `browser_missing`, `renderer_dependency`, or
`browser_sandbox_or_permissions`; document contents are never logged.

Test editing a sample profile, live preview, and a multi-page PDF after setup;
inspect the error log if these fail. No production rendering validation has
been performed on this account.

Official references:
- [Flask deployment](https://help.pythonanywhere.com/pages/Flask/)
- [Playwright on PythonAnywhere](https://help.pythonanywhere.com/pages/Playwright/)
