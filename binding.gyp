{
  'variables': {
    'vips_version': '8.9.0',
    'sharp_vendor_dir': '<(module_root_dir)/vendor/<@(vips_version)'
  },
  'targets': [{
    'target_name': 'libvips-cpp',
    'conditions': [
      ['OS == "win"', {
        # Build libvips C++ binding for Windows due to MSVC std library ABI changes
        'type': 'shared_library',
        'defines': [
          'VIPS_CPLUSPLUS_EXPORTS',
          '_ALLOW_KEYWORD_MACROS'
        ],
        'sources': [
          'src/libvips/cplusplus/VError.cpp',
          'src/libvips/cplusplus/VConnection.cpp',
          'src/libvips/cplusplus/VInterpolate.cpp',
          'src/libvips/cplusplus/VImage.cpp'
        ],
        'include_dirs': [
          '<(sharp_vendor_dir)/include',
          '<(sharp_vendor_dir)/include/glib-2.0',
          '<(sharp_vendor_dir)/lib/glib-2.0/include'
        ],
        'libraries': [
          'libvips.lib',
          'libglib-2.0.lib',
          'libgobject-2.0.lib'
        ],
        'library_dirs': ['<(sharp_vendor_dir)/lib'],
        'configurations': {
          'Release': {
            'msvs_settings': {
              'VCCLCompilerTool': {
                'ExceptionHandling': 1
              }
            },
            'msvs_disabled_warnings': [
              4275
            ]
          }
        }
      }, {
        # Ignore this target for non-Windows
        'type': 'none'
      }]
    ]
  }, {
    'target_name': 'sharp',
    'dependencies': [
      'libvips-cpp'
    ],
    'variables': {
      'runtime_link%': 'shared',
      'conditions': [
        ['OS != "win"', {
          'pkg_config_path': '<!(node -e "console.log(require(\'./lib/libvips\').pkgConfigPath())")',
          'use_global_libvips': '<!(node -e "console.log(Boolean(require(\'./lib/libvips\').useGlobalLibvips()).toString())")'
        }, {
          'pkg_config_path': '',
          'use_global_libvips': ''
        }]
      ]
    },
    'sources': [
      'src/common.cc',
      'src/metadata.cc',
      'src/stats.cc',
      'src/operations.cc',
      'src/pipeline.cc',
      'src/sharp.cc',
      'src/utilities.cc'
    ],
    'include_dirs': [
      '<!(node -e "require(\'nan\')")'
    ],
    'conditions': [
      ['use_global_libvips == "true"', {
        # Use pkg-config for include and lib
        'include_dirs': ['<!@(PKG_CONFIG_PATH="<(pkg_config_path)" pkg-config --cflags-only-I vips-cpp vips glib-2.0 | sed s\/-I//g)'],
        'conditions': [
          ['runtime_link == "static"', {
            'libraries': ['<!@(PKG_CONFIG_PATH="<(pkg_config_path)" pkg-config --libs --static vips-cpp)']
          }, {
            'libraries': ['<!@(PKG_CONFIG_PATH="<(pkg_config_path)" pkg-config --libs vips-cpp)']
          }],
          ['OS == "linux"', {
            'defines': [
              # Inspect libvips-cpp.so to determine which C++11 ABI version was used and set _GLIBCXX_USE_CXX11_ABI accordingly. This is quite horrible.
              '_GLIBCXX_USE_CXX11_ABI=<!(if readelf -Ws "$(PKG_CONFIG_PATH="<(pkg_config_path)" pkg-config --variable libdir vips-cpp)/libvips-cpp.so" | c++filt | grep -qF __cxx11;then echo "1";else echo "0";fi)'
            ]
          }]
        ]
      }, {
        # Use pre-built libvips stored locally within node_modules
        'include_dirs': [
          '<(sharp_vendor_dir)/include',
          '<(sharp_vendor_dir)/include/glib-2.0',
          '<(sharp_vendor_dir)/lib/glib-2.0/include'
        ],
        'conditions': [
          ['OS == "win"', {
            'defines': [
              '_ALLOW_KEYWORD_MACROS',
              '_FILE_OFFSET_BITS=64'
            ],
            'libraries': [
              'libvips.lib',
              'libglib-2.0.lib',
              'libgobject-2.0.lib'
            ],
            'library_dirs': ['<(sharp_vendor_dir)/lib']
          }],
          ['OS == "mac"', {
            'libraries': [
              'libvips-cpp.42.dylib',
              'libvips.42.dylib',
              'libglib-2.0.0.dylib',
              'libgobject-2.0.0.dylib'
            ],
            'library_dirs': ['<(sharp_vendor_dir)/lib'],
            'xcode_settings': {
              'OTHER_LDFLAGS': [
                # Ensure runtime linking is relative to sharp.node
                '-Wl,-rpath,\'@loader_path/../../vendor\''
              ]
            }
          }],
          ['OS == "linux"', {
            'defines': [
              '_GLIBCXX_USE_CXX11_ABI=0'
            ],
            'libraries': [
              '-l:libvips-cpp.so.52',
              '-l:libvips.so.52',
              '-l:libglib-2.0.so.0',
              '-l:libgobject-2.0.so.0',
              # Dependencies of dependencies, included for openSUSE support
              '-l:libcairo.so.2',
              '-l:libexif.so.12',
              '-l:libexpat.so.1',
              '-l:libffi.so.7',
              '-l:libfontconfig.so.1',
              '-l:libfreetype.so.6',
              '-l:libfribidi.so.0',
              '-l:libgdk_pixbuf-2.0.so.0',
              '-l:libgif.so.7',
              '-l:libgio-2.0.so.0',
              '-l:libgmodule-2.0.so.0',
              '-l:libgsf-1.so.114',
              '-l:libgthread-2.0.so.0',
              '-l:libharfbuzz.so.0',
              '-l:libjpeg.so.8',
              '-l:liblcms2.so.2',
              '-l:liborc-0.4.so.0',
              '-l:libpango-1.0.so.0',
              '-l:libpangocairo-1.0.so.0',
              '-l:libpangoft2-1.0.so.0',
              '-l:libpixman-1.so.0',
              '-l:libpng16.so.16',
              '-l:librsvg-2.so.2',
              '-l:libtiff.so.5',
              '-l:libwebp.so.7',
              '-l:libwebpdemux.so.2',
              '-l:libwebpmux.so.3',
              '-l:libxml2.so.2',
              '-l:libz.so.1'
            ],
            'library_dirs': ['<(sharp_vendor_dir)/lib'],
            'ldflags': [
              # Ensure runtime linking is relative to sharp.node
              '-Wl,--disable-new-dtags -Wl,-rpath=\'$$ORIGIN/../../vendor/<(vips_version)/lib\''
            ]
          }]
        ]
      }]
    ],
    'cflags_cc': [
      '-std=c++0x',
      '-fexceptions',
      '-Wall',
      '-O3'
    ],
    'xcode_settings': {
      'CLANG_CXX_LANGUAGE_STANDARD': 'c++11',
      'CLANG_CXX_LIBRARY': 'libc++',
      'MACOSX_DEPLOYMENT_TARGET': '10.7',
      'GCC_ENABLE_CPP_EXCEPTIONS': 'YES',
      'GCC_ENABLE_CPP_RTTI': 'YES',
      'OTHER_CPLUSPLUSFLAGS': [
        '-fexceptions',
        '-Wall',
        '-O3'
      ]
    },
    'configurations': {
      'Release': {
        'conditions': [
          ['OS == "linux"', {
            'cflags_cc': [
              '-Wno-cast-function-type'
            ]
          }],
          ['OS == "win"', {
            'msvs_settings': {
              'VCCLCompilerTool': {
                'ExceptionHandling': 1
              }
            },
            'msvs_disabled_warnings': [
              4275
            ]
          }]
        ]
      }
    },
  }]
}
