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
CHROMIUM_SANDBOX=false
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

The supplied direct preview test reached Chromium and failed with
`browser_sandbox_or_permissions`. PythonAnywhere documents using its preinstalled
`/usr/bin/chromium` instead of `playwright install`, with `--no-sandbox`.
Set `CHROMIUM_SANDBOX=false` in this host's `.env` to use that launch mode, then
reload the web app. Playwright adds `--no-sandbox` when `chromium_sandbox=False`.

This explicitly removes Chromium's own process sandbox, reducing defense in
depth against browser vulnerabilities. The renderer still blocks page network
requests, disables page JavaScript and service workers, uses generated escaped
HTML and normalized images, and enforces a subprocess timeout. Those safeguards
are not a replacement for OS-level browser isolation. Use a separate isolated
rendering environment if Chromium's sandbox is required by your deployment.
The default remains enabled on all hosts; only the exact environment value
`false` disables it. Profile data cannot change this setting, and failed launches
never automatically retry without a sandbox.

The worker uses the explicit virtualenv interpreter above, avoiding the embedded
uWSGI executable. Renderer errors are logged as safe
categories such as `browser_missing`, `renderer_dependency`, or
`browser_sandbox_or_permissions`; document contents are never logged.

Test editing a sample profile, live preview, and a multi-page PDF after setup;
inspect the error log if these fail. No production rendering validation has
been performed on this account.

Official references:
- [Flask deployment](https://help.pythonanywhere.com/pages/Flask/)
- [Playwright on PythonAnywhere](https://help.pythonanywhere.com/pages/Playwright/)
