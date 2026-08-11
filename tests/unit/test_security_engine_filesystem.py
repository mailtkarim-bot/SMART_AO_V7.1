"""
SMART_AO V7 - Tests unitaires complets pour filesystem.py
==========================================================
Tests pour les fonctions de validation de fichiers.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile

from app.engines.security_engine.filesystem import (
    get_file_extension,
    validate_file_extension,
    validate_file_size,
    validate_file_type,
    validate_file_content,
    validate_upload_file,
    validate_file,
    HAS_MAGIC,
)


class TestGetFileExtension:
    """Tests pour get_file_extension."""

    def test_pdf_extension(self):
        assert get_file_extension("document.pdf") == ".pdf"

    def test_uppercase_extension(self):
        assert get_file_extension("document.PDF") == ".pdf"

    def test_no_extension(self):
        assert get_file_extension("document") == ""

    def test_multiple_dots(self):
        assert get_file_extension("archive.tar.gz") == ".gz"

    def test_path_with_directory(self):
        assert get_file_extension("/path/to/document.pdf") == ".pdf"


class TestValidateFileExtension:
    """Tests pour validate_file_extension."""

    @patch('app.engines.security_engine.filesystem.settings')
    def test_valid_extension(self, mock_settings):
        mock_settings.UPLOAD_ALLOWED_EXTENSIONS = ".pdf,.docx,.json"
        valid, message = validate_file_extension("document.pdf")
        assert valid is True

    @patch('app.engines.security_engine.filesystem.settings')
    def test_invalid_extension(self, mock_settings):
        mock_settings.UPLOAD_ALLOWED_EXTENSIONS = ".pdf,.docx"
        valid, message = validate_file_extension("script.js")
        assert valid is False
        # Vérifier que le message mentionne .js
        assert ".js" in message.lower()


class TestValidateFileSize:
    """Tests pour validate_file_size."""

    @patch('app.engines.security_engine.filesystem.settings')
    def test_valid_size(self, mock_settings):
        mock_settings.UPLOAD_MAX_SIZE_MB = 10
        valid, message = validate_file_size(5 * 1024 * 1024)
        assert valid is True

    @patch('app.engines.security_engine.filesystem.settings')
    def test_too_large_size(self, mock_settings):
        mock_settings.UPLOAD_MAX_SIZE_MB = 10
        valid, message = validate_file_size(15 * 1024 * 1024)
        assert valid is False


class TestValidateFileType:
    """Tests pour validate_file_type."""

    def test_without_magic(self):
        if not HAS_MAGIC:
            valid, message = validate_file_type(b"content", "document.pdf")
            assert valid is True
            # Vérifier que le message mentionne magic
            assert "magic" in message.lower()

    def test_with_magic(self):
        if HAS_MAGIC:
            pdf_content = b'%PDF-1.4\n\x00\x00\x00\x00'
            valid, message = validate_file_type(pdf_content, "document.pdf")
            assert isinstance(valid, bool)


class TestValidateFileContent:
    """Tests pour validate_file_content."""

    def test_clean_text_content(self):
        clean_content = b"Ceci est un contenu texte normal."
        valid, message = validate_file_content(clean_content, "document.txt")
        assert valid is True

    def test_suspicious_php_content(self):
        php_content = b'<?php echo "malicious"; ?>'
        valid, message = validate_file_content(php_content, "script.php")
        assert valid is False

    def test_suspicious_javascript(self):
        js_content = b'<script>alert("xss")</script>'
        valid, message = validate_file_content(js_content, "script.js")
        assert valid is False

    def test_suspicious_eval(self):
        eval_content = b'result = eval(user_input)'
        valid, message = validate_file_content(eval_content, "script.txt")
        assert valid is False

    def test_suspicious_system(self):
        system_content = b'os.system("rm -rf /")'
        valid, message = validate_file_content(system_content, "script.txt")
        assert valid is False

    def test_binary_content(self):
        pdf_content = b'%PDF-1.4\x00\x00\x00\x00'
        valid, message = validate_file_content(pdf_content, "document.pdf")
        assert valid is True

    def test_empty_content(self):
        valid, message = validate_file_content(b'', "document.txt")
        assert valid is True


class TestValidateFile:
    """Tests pour validate_file (synchrone)."""

    def test_valid_file(self):
        content = b"Clean content"
        valid, message = validate_file(content, "document.txt")
        assert valid is True

    def test_invalid_content(self):
        content = b'<?php echo "malicious"; ?>'
        valid, message = validate_file(content, "script.php")
        assert valid is False


class TestValidateUploadFile:
    """Tests pour validate_upload_file (asynchrone)."""

    @patch('app.engines.security_engine.filesystem.validate_file_extension')
    @patch('app.engines.security_engine.filesystem.validate_file_size')
    @patch('app.engines.security_engine.filesystem.validate_file_type')
    @patch('app.engines.security_engine.filesystem.validate_file_content')
    @pytest.mark.asyncio
    async def test_all_valid(self, mock_content, mock_type, mock_size, mock_ext):
        mock_ext.return_value = (True, "Extension valide")
        mock_size.return_value = (True, "Taille valide")
        mock_type.return_value = (True, "Type valide")
        mock_content.return_value = (True, "Contenu valide")
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.size = 1024
        
        result = await validate_upload_file(mock_file)
        assert result[0] is True

    @patch('app.engines.security_engine.filesystem.validate_file_extension')
    @patch('app.engines.security_engine.filesystem.validate_file_size')
    @pytest.mark.asyncio
    async def test_extension_invalid(self, mock_size, mock_ext):
        mock_ext.return_value = (False, "Extension invalide")
        mock_size.return_value = (True, "Taille valide")
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "script.js"
        mock_file.size = 1024
        
        result = await validate_upload_file(mock_file)
        assert result[0] is False


class TestHasMagic:
    """Tests pour HAS_MAGIC."""

    def test_has_magic_is_boolean(self):
        assert isinstance(HAS_MAGIC, bool)
