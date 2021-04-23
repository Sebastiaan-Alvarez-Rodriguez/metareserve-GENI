import setuptools
import os


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    f = open(path)
    return f.read()

install_requires = [x for x in read('requirements.txt').strip().split('\n') if x]

setuptools.setup(
    name='metareserve-GENI',
    version='0.1.0',
    author='Sebastiaan Alvarez Rodriguez',
    author_email='a@b.c',
    description='GENI Plugin for metareserve reservation system',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve-GENI',
    packages=setuptools.find_packages(),#where='metareserve_geni'),
    # package_dir={'': 'metareserve_geni'},
    classifiers=(
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'geni-reserve = metareserve_geni.cli.cli:main',
            ],
        # 'metareserve-GENI.cli.main': [
        # ]
        # 'ceph_deploy.cli': [
        #     'new = ceph_deploy.new:make',
        #     'install = ceph_deploy.install:make',
        #     'uninstall = ceph_deploy.install:make_uninstall',
        #     'purge = ceph_deploy.install:make_purge',
        #     'purgedata = ceph_deploy.install:make_purge_data',
        #     'mon = ceph_deploy.mon:make',
        #     'gatherkeys = ceph_deploy.gatherkeys:make',
        #     'osd = ceph_deploy.osd:make',
        #     'disk = ceph_deploy.osd:make_disk',
        #     'mds = ceph_deploy.mds:make',
        #     'mgr = ceph_deploy.mgr:make',
        #     'forgetkeys = ceph_deploy.forgetkeys:make',
        #     'config = ceph_deploy.config:make',
        #     'admin = ceph_deploy.admin:make',
        #     'pkg = ceph_deploy.pkg:make',
        #     'rgw = ceph_deploy.rgw:make',
        #     'repo = ceph_deploy.repo:make',
        #     ],
    },
)