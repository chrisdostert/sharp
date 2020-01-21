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
              'libgobject-2.0.0.dylib',
            ],
            'library_dirs': ['<(sharp_vendor_dir)/lib'],
            'ldflags': [
              # Ensure runtime linking is relative to sharp.node
              '-rpath \'../../vendor/<(vips_version)/lib\''
            ]
          }],
          ['OS == "linux"', {
            'defines': [
              '_GLIBCXX_USE_CXX11_ABI=0'
            ],
            'libraries': [
              '-lvips-cpp',
              '-lvips',
              '-lglib-2.0',
              '-lgobject-2.0',
              # Dependencies of dependencies, included for openSUSE support
              '-lcairo',
              '-lexif',
              '-lexpat',
              '-lffi',
              '-lfontconfig',
              '-lfreetype',
              '-lfribidi',
              '-lgdk_pixbuf-2.0',
              '-lgif',
              '-lgio-2.0',
              '-lgmodule-2.0',
              '-lgsf-1',
              '-lgthread-2.0',
              '-lharfbuzz',
              '-ljpeg',
              '-llcms2',
              '-lorc-0.4',
              '-lpango-1.0',
              '-lpangocairo-1.0',
              '-lpangoft2-1.0',
              '-lpixman-1',
              '-lpng',
              '-lrsvg-2',
              '-ltiff',
              '-lwebp',
              '-lwebpdemux',
              '-lwebpmux',
              '-lxml2',
              '-lz',
            ],
            'library_dirs': ['<(sharp_vendor_dir)/lib'],
            'ldflags': [
              # Ensure runtime linking is relative to sharp.node
              '-Wl,--disable-new-dtags -Wl,-rpath=\'../../vendor/<(vips_version)/lib\''
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
