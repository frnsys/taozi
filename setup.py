from setuptools import setup

setup(
    name='taozi',
    version='0.0.4',
    description='simple CMS for flask',
    url='https://github.com/frnsys/taozi',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',
    include_package_data=True,
    packages=['taozi'],
    install_requires=[
        'Flask-Login==0.6.2',
        'Flask-Security-Too==4.1.6',
        'Flask-SQLAlchemy==2.5.1',
        'Flask-Migrate==2.3.1',
        'Flask-WTF==1.2.1 ',
        'python-slugify==2.0.1',
        'Markdown==3.4.2',
        'py-gfm==2.0.0',
        'bcrypt==3.1.6',
        'Flask==2.0.3',
        'Flask-Mail==0.9.1',
        'Pillow==9.0.1',
        'SQLAlchemy==1.3.3',
        'python-slugify==2.0.1',
        'Whoosh==2.7.4',
        'Werkzeug==2.2.0',
        'WTForms==3.1.1',
        'WTForms-SQLAlchemy==0.3'
    ]
)

