"""One subprocess per export; browser/network/storage isolation is deliberately explicit."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    job = json.load(sys.stdin)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=job.get('executable'),
                                             chromium_sandbox=True)
        try:
            context = browser.new_context(java_script_enabled=False, service_workers='block')
            context.route('**/*', lambda route: route.abort())
            page = context.new_page()
            page.set_viewport_size({'width': 794, 'height': 1123})
            page.emulate_media(media='print')
            page.set_default_timeout(20000)
            page.set_content(job['html'], wait_until='load')
            page.evaluate('document.fonts.ready')
            if page.locator('.craft-document').count():
                paginator = Path(__file__).resolve().parents[1] / 'static/js/collection-paginator.js'
                page.evaluate(paginator.read_text())
            else:
                page.evaluate('''() => {
                    const style = getComputedStyle(document.querySelector('.biodata'));
                    const usableHeight = 297 * 96 / 25.4 - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
                    document.querySelectorAll('.doc-section').forEach(section => {
                        if (section.getBoundingClientRect().height > usableHeight)
                            section.classList.add('oversized-section');
                    });
                }''')
            output = page.pdf(format='A4', print_background=True, prefer_css_page_size=True, tagged=True,
                              margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
            sys.stdout.buffer.write(output)
        finally:
            browser.close()


if __name__ == '__main__':
    main()
