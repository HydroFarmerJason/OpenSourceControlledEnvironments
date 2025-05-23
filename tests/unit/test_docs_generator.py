from unittest.mock import patch

from src.docs.generator import DocumentationGenerator


def test_generate_api_docs_invokes_sphinx():
    with patch('src.docs.generator.sphinx_build') as mock_build:
        docgen = DocumentationGenerator()
        docgen.generate_api_docs()
        assert mock_build.called
