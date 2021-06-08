from setuptools import setup

setup(
    name='taozi',
    version='0.0.3',
    description='simple CMS for flask',
    url='https://github.com/frnsys/taozi',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',
    include_package_data=True,
    packages=['taozi'],
    install_requires=[
        'Flask-Security==3.0.0',
        'Flask-SQLAlchemy==2.3.2',
        'Flask-Migrate==2.3.1',
        'Flask-WTF==0.14.2',
        'python-slugify==2.0.1',
        'Markdown==2.6.11',
        'py-gfm==0.1.1',
        'bcrypt==3.1.6',
        'Flask==1.0.2',
        'Flask-Mail==0.9.1',
        'Pillow==8.2.0',
        'SQLAlchemy==1.3.3',
        'python-slugify==2.0.1',
        'Whoosh==2.7.4'
    ]
)

