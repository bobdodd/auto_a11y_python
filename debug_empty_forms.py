import asyncio
from pyppeteer import launch
import json

async def debug_empty_forms():
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    fixture_path = '/Users/bob3/Desktop/auto_a11y_python/Fixtures/Forms/ErrFormEmptyHasNoChildNodes_001_violations_basic.html'
    await page.goto(f'file://{fixture_path}')

    result = await page.evaluate('''() => {
        const results = {
            errors: [],
            elements_failed: 0
        };

        function getFullXPath(element) {
            if (element.id !== '') {
                return 'id("' + element.id + '")';
            }
            if (element === document.body) {
                return '/html/body';
            }
            let ix = 0;
            const siblings = element.parentNode ? element.parentNode.childNodes : [];
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) {
                    return getFullXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
            return '';
        }

        console.log('=== Starting empty forms check ===');

        const allForms = Array.from(document.querySelectorAll('form'));
        console.log('Found forms:', allForms.length);

        allForms.forEach((form, index) => {
            console.log(`\\nForm ${index}:`);
            console.log('  childNodes.length:', form.childNodes.length);
            console.log('  innerHTML:', form.innerHTML);
            console.log('  outerHTML:', form.outerHTML.substring(0, 100));

            if (form.childNodes.length === 0) {
                console.log('  -> PUSHING ERROR for empty form');
                results.errors.push({
                    err: 'ErrFormEmptyHasNoChildNodes',
                    type: 'err',
                    cat: 'forms',
                    element: 'FORM',
                    xpath: getFullXPath(form),
                    html: form.outerHTML.substring(0, 200),
                    description: 'Form element is completely empty with no child nodes'
                });
                results.elements_failed++;
                console.log('  -> Error pushed. Total errors now:', results.errors.length);
            } else {
                console.log('  -> Form is NOT empty, skipping');
            }
        });

        console.log('\\n=== Final results ===');
        console.log('Total errors:', results.errors.length);
        console.log('Elements failed:', results.elements_failed);

        return results;
    }''')

    print("\n=== Python received ===")
    print(f"Total errors: {len(result['errors'])}")
    print(f"Elements failed: {result['elements_failed']}")

    if result['errors']:
        print("\nErrors found:")
        for i, error in enumerate(result['errors']):
            print(f"\n{i+1}. {error['err']}")
            print(f"   Description: {error['description']}")
            print(f"   XPath: {error['xpath']}")
    else:
        print("\nNO ERRORS FOUND")

    await browser.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(debug_empty_forms())
