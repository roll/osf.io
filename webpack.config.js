var path = require('path');
var fs = require('fs');
var webpack = require('webpack');

var addons = require('./addons.json');
var root = path.join(__dirname, 'website', 'static');
/** Return the absolute path given a path relative to ./website/static */
var staticPath = function(dir) {
    return path.join(root, dir);
};

var entry = {
    'dashboard': staticPath('js/pages/dashboard-page.js'),
    'profile': staticPath('js/pages/profile-page.js'),
    'project-dashboard': staticPath('js/pages/project-dashboard-page.js'),
    'project-base': staticPath('js/pages/project-base-page.js'),
    'wiki-edit-page': staticPath('js/pages/wiki-edit-page.js'),
    // TODO: Optimize common chunks between these modules
    'files-page': staticPath('js/pages/files-page.js'),
    // Commons chunk
    'vendor': [
        'knockout',
        'bootstrap',
        'bootbox',
        'hgrid',
        staticPath('vendor/knockout-punches/knockout.punches.js'),
        staticPath('vendor/bower_components/dropzone/downloads/dropzone.js'),
        staticPath('vendor/knockout-punches/knockout.punches.js'),
        staticPath('vendor/knockout-sortable/knockout-sortable.js'),
        staticPath('js/dropzone-patch.js'),
        staticPath('js/osf-helpers.js'),
        staticPath('js/rubeus.js')
    ]
};

// Collect adddons endpoints. If an addon's static folder has
// any of the following files, it will be added as an entry point
// and output to website/static/public/js/<addon-name>/files.js
var addonModules = ['files.js', 'node-cfg.js', 'user-cfg.js'];
addons.addons.forEach(function(addonName) {
    var baseDir = addonName + '/';
    addonModules.forEach(function(module) {
        var modulePath = path.join(__dirname, 'website', 'addons', 
                                  addonName, 'static', module);
        if (fs.existsSync(modulePath)) {
            var entryPoint = baseDir + module.split('.')[0];
            entry[entryPoint] =  modulePath;
        }
    });
});

module.exports = {
    // Split code chunks by page
    entry: entry,
    debug: true,
    output: {
        path: './website/static/public/js/',
        // publicPath: '/static/', // used to generate urls to e.g. images
        filename: '[name].js'
    },
    resolve: {
        root: root,
        // Look for required files in bower and npm directories
        modulesDirectories: ['./website/static/vendor/bower_components', 'node_modules'],
        // Need to alias libraries that aren't managed by bower or npm
        alias: {
            'knockout-punches': staticPath('vendor/knockout-punches/knockout.punches.js'),
            'knockout-sortable': staticPath('vendor/knockout-sortable/knockout-sortable.js'),
            'knockout-validation': staticPath('vendor/knockout-validation/knockout.validation.min.js'),
            'knockout-mapping': staticPath('vendor/knockout-mapping/knockout.mapping.js'),
            'bootstrap-editable': staticPath('vendor/bootstrap3-editable/js/bootstrap-editable.js'),
            'zeroclipboard': staticPath('vendor/bower_components/zeroclipboard/dist/ZeroClipboard.js'),
            // Needed for knockout-sortable
            'jquery.ui.sortable': staticPath('vendor/bower_components/jquery-ui/ui/jquery.ui.sortable.js'),
            // Dropzone doesn't have a proper 'main' entry in its bower.json
            'dropzone': staticPath('vendor/bower_components/dropzone/downloads/dropzone.js'),
            // Also alias some internal libraries for easy access
            'dropzone-patch': staticPath('js/dropzone-patch.js'),
            'rubeus': staticPath('js/rubeus.js'),
            'folderpicker': staticPath('js/folderPicker.js'),
            'osf-helpers': staticPath('js/osf-helpers.js'),
            'osf-language': staticPath('js/osf-language.js'),
            'addons': path.join(__dirname, 'website', 'addons')
        }
    },
    plugins: [
        // Bundle common code between modules
        new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js'),
        // Bower support
        new webpack.ResolverPlugin(
            new webpack.ResolverPlugin.DirectoryDescriptionFilePlugin('bower.json', ['main'])
        ),
        // Make jQuery available in all modules without having to do require('jquery')
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
        // Slight hack to make sure that CommonJS is always used
        new webpack.DefinePlugin({
            'define.amd': false
        })
    ],
    externals: {
        // require("jquery") is external and available
        //  on the global var jQuery, which is loaded with CDN
        'jquery': 'jQuery',
        'jquery-ui': 'jQuery.ui'
    }
};
