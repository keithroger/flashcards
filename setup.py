from setuptools import setup, find_packages

setup(
    name='flashcards',
    version='0.2.0',
    description='A simple flashcard program',
    url='https://github.com/keithroger/flashcards',
    author='Keith Ontiveros',
    author_email='keithontiveros@ucla.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Kivy==2.0.0',
        'kivymd==0.104.2',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    package_data={'flashcards': ['decks/*.csv', 'screens.kv']},
    entry_points={
        'console_scripts': ['flashcards = flashcards.gui:main']
    }
)
