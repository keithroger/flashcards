from setuptools import setup

setup(
    name='flashcards',
    version='0.2.0',
    description='A simple flashcard program',
    url='https://github.com/keithroger/flashcards',
    author='Keith Ontiveros',
    author_email='keithontiveros@ucla.edu',
    license='MIT',
    packages=['flashcards'],
    install_requires=[
        'Kivy==2.0.0',
#         'kivymd==0.104.2',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['flashcards = flashcards.gui:main']
    }
)
