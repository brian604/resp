import setuptools
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Core dependencies
install_requires = [
    'beautifulsoup4>=4.11.1',
    'requests>=2.28.1',
    'pandas>=1.3.0',
    'numpy>=1.21.0',
    'tqdm>=4.64.0',
    'google-search-results>=2.4.1',
    'pybtex>=0.24.0',
    'latexcodec>=2.0.1',
    'selenium>=4.2.0',
    'PySocks>=1.7.1',
    'PyYAML>=6.0',
    'python-dateutil>=2.8.2',
    'pytz>=2022.1',
]

# Optional dependencies for AI summarization
summarization_deps = [
    'openai>=1.0.0',
]

local_models_deps = [
    'transformers>=4.30.0',
    'torch>=2.0.0',
]

# Optional dependencies for semantic search
semantic_search_deps = [
    'sentence-transformers>=2.2.0',
    'faiss-cpu>=1.7.4',
]

setup(
    name='resp',
    version='0.2.0',
    description='Research Papers Search, Summarization, and Semantic Search',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ankit Pal',
    packages=setuptools.find_packages(
        where=".",
        exclude=("examples",),
    ),
    project_urls={
        "GitHub": "https://github.com/monk1337/resp",
    },
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'summarization': summarization_deps,
        'local': local_models_deps,
        'semantic': semantic_search_deps,
        'all': summarization_deps + local_models_deps + semantic_search_deps,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)