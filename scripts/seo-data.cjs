/* Read the existing, public translation dictionaries without a browser. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const context = vm.createContext({window: {}});
for (const name of ['content', 'v5-data', 'locales', 'article-data', 'routes']) {
  vm.runInContext(fs.readFileSync(path.join(root, 'static/hw/js', name + '.js'), 'utf8'), context,
    {filename: name + '.js', timeout: 5000});
}
process.stdout.write(JSON.stringify(context.window));
