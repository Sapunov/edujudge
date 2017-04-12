module.exports = function(grunt) {
  'use strict';

  grunt.initConfig({
    concat: {
        options: {
          separator: ';',
        },
        dist: {
          src: [
            'app/judge/ui/static/js/common.js',
            'app/judge/ui/static/js/init.js',
            'app/judge/ui/static/js/controllers.js',
            'app/judge/ui/static/js/app.js',
            'app/judge/ui/static/js/directives.js'
          ],
          dest: 'app/judge/ui/static/app.js',
        },
    },
    watch: {
      options: {
        livereload: false,
      },
      concat_js: {
        files: [
          'app/judge/ui/static/js/*'
        ],
        tasks: ['concat:dist']
      }
    },
  });

  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', ['concat', 'watch']);
};
