from setuptools import setup

setup(
    name='flashcards',
    version='1.0',
    description='A simple flashcard program',
    author='Keith Ontiveros',
    author_email='keithontiveros@ucla.edu',
    license='MIT',
    packages=['flashcards'],
    install_requires=[
        'Kivy==2.0.0',
        'kivymd==0.104.2',
    ],
    python_requires='>=3.7',
)
