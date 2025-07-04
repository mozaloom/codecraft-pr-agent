#!/usr/bin/env python3
"""
Unit tests for Module 1: Basic MCP Server
"""

import json
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from server import (
    mcp,
    analyze_file_changes,
    get_pr_templates,
    suggest_template,
    TEMPLATES_DIR
)


class TestAnalyzeFileChanges:
    """Test the analyze_file_changes tool."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_diff(self):
        """Test analyzing changes with full diff included."""
        mock_result = MagicMock()
        mock_result.stdout = "M\tfile1.py\nA\tfile2.py\n"
        mock_result.stderr = ""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = mock_result
            
            result = await analyze_file_changes("main", include_diff=True)
            
            assert isinstance(result, str)
            data = json.loads(result)
            assert data["base_branch"] == "main"
            assert "files_changed" in data
            assert "statistics" in data
            assert "commits" in data
            assert "diff" in data
    
    @pytest.mark.asyncio
    async def test_analyze_without_diff(self):
        """Test analyzing changes without diff content."""
        mock_result = MagicMock()
        mock_result.stdout = "M\tfile1.py\n"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = mock_result
            
            result = await analyze_file_changes("main", include_diff=False)
            
            data = json.loads(result)
            assert "Diff not included" in data["diff"]
    @pytest.mark.asyncio
    async def test_analyze_git_error(self):
        """Test handling git command errors."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git not found")

            result = await analyze_file_changes("main", True)

            assert "error" in result
            data = json.loads(result)
            assert "error" in data


class TestPRTemplates:
    """Test PR template management."""
    
    @pytest.mark.asyncio
    async def test_get_templates(self, tmp_path, monkeypatch):
        """Test getting available templates."""
        # Use temporary directory for templates
        monkeypatch.setattr('server.TEMPLATES_DIR', tmp_path)
        
        # Create some test template files
        (tmp_path / "bug.md").write_text("## Bug Fix Template\n\nDescription:\n\nRoot Cause:\n")
        (tmp_path / "feature.md").write_text("## Feature Template\n\nDescription:\n\nChanges:\n")
        (tmp_path / "docs.md").write_text("## Documentation Template\n\nChanges:\n")
        (tmp_path / "refactor.md").write_text("## Refactor Template\n\nChanges:\n")
        (tmp_path / "test.md").write_text("## Test Template\n\nChanges:\n")
        (tmp_path / "performance.md").write_text("## Performance Template\n\nChanges:\n")
        (tmp_path / "security.md").write_text("## Security Template\n\nChanges:\n")

        result = await get_pr_templates()

        templates = json.loads(result)
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert any(t["type"] == "Bug Fix" for t in templates)
        assert any(t["type"] == "Feature" for t in templates)
        assert all("content" in t for t in templates)


class TestSuggestTemplate:
    """Test template suggestion based on analysis."""
    
    @pytest.mark.asyncio
    async def test_suggest_bug_fix(self, tmp_path, monkeypatch):
        """Test suggesting bug fix template."""
        monkeypatch.setattr('server.TEMPLATES_DIR', tmp_path)
        
        # Create template files
        (tmp_path / "bug.md").write_text("## Bug Fix Template\n\nDescription:\n\nRoot Cause:\n")
        (tmp_path / "feature.md").write_text("## Feature Template\n\nDescription:\n\nChanges:\n")
        (tmp_path / "docs.md").write_text("## Documentation Template\n\nChanges:\n")
        (tmp_path / "refactor.md").write_text("## Refactor Template\n\nChanges:\n")
        (tmp_path / "test.md").write_text("## Test Template\n\nChanges:\n")
        (tmp_path / "performance.md").write_text("## Performance Template\n\nChanges:\n")
        (tmp_path / "security.md").write_text("## Security Template\n\nChanges:\n")
        
        result = await suggest_template(
            "Fixed null pointer exception in user service",
            "bug"
        )
        
        suggestion = json.loads(result)
        assert "recommended_template" in suggestion
        assert suggestion["recommended_template"]["filename"] == "bug.md"
        assert "Bug Fix" in suggestion["recommended_template"]["type"]
        assert "reasoning" in suggestion
    @pytest.mark.asyncio
    async def test_suggest_feature(self, tmp_path, monkeypatch):
        """Test suggesting feature template."""
        monkeypatch.setattr('server.TEMPLATES_DIR', tmp_path)
        
        # Create template files
        (tmp_path / "bug.md").write_text("## Bug Fix Template\n\nDescription:\n\nRoot Cause:\n")
        (tmp_path / "feature.md").write_text("## Feature Template\n\nDescription:\n\nChanges:\n")
        (tmp_path / "docs.md").write_text("## Documentation Template\n\nChanges:\n")
        (tmp_path / "refactor.md").write_text("## Refactor Template\n\nChanges:\n")
        (tmp_path / "test.md").write_text("## Test Template\n\nChanges:\n")
        (tmp_path / "performance.md").write_text("## Performance Template\n\nChanges:\n")
        (tmp_path / "security.md").write_text("## Security Template\n\nChanges:\n")

        result = await suggest_template(
            "Added new authentication method for API",
            "feature"
        )

        suggestion = json.loads(result)
        assert "recommended_template" in suggestion
        assert suggestion["recommended_template"]["filename"] == "feature.md"
    
    @pytest.mark.asyncio
    async def test_suggest_with_type_variations(self, tmp_path, monkeypatch):
        """Test template suggestion with various type names."""
        monkeypatch.setattr('server.TEMPLATES_DIR', tmp_path)
        
        # Create template files
        (tmp_path / "bug.md").write_text("## Bug Fix Template\n\nDescription:\n\nRoot Cause:\n")
        (tmp_path / "feature.md").write_text("## Feature Template\n\nDescription:\n\nChanges:\n")
        (tmp_path / "docs.md").write_text("## Documentation Template\n\nChanges:\n")
        (tmp_path / "refactor.md").write_text("## Refactor Template\n\nChanges:\n")
        (tmp_path / "test.md").write_text("## Test Template\n\nChanges:\n")
        (tmp_path / "performance.md").write_text("## Performance Template\n\nChanges:\n")
        (tmp_path / "security.md").write_text("## Security Template\n\nChanges:\n")
        
        # Test variations
        for change_type, expected_file in [
            ("fix", "bug.md"),
            ("enhancement", "feature.md"),
            ("documentation", "docs.md"),
            ("cleanup", "refactor.md"),
            ("testing", "test.md"),
            ("optimization", "performance.md")
        ]:
            result = await suggest_template(f"Some {change_type} work", change_type)
            suggestion = json.loads(result)
            assert "recommended_template" in suggestion
            assert suggestion["recommended_template"]["filename"] == expected_file


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, tmp_path, monkeypatch):
        """Test the complete workflow from analysis to suggestion."""
        monkeypatch.setattr('server.TEMPLATES_DIR', tmp_path)
        
        # Create template files
        (tmp_path / "bug.md").write_text("## Bug Fix Template\n\nDescription:\n\nRoot Cause:\n")
        (tmp_path / "feature.md").write_text("## Feature Template\n\nDescription:\n\nChanges:\n")
        (tmp_path / "docs.md").write_text("## Documentation Template\n\nChanges:\n")
        (tmp_path / "refactor.md").write_text("## Refactor Template\n\nChanges:\n")
        (tmp_path / "test.md").write_text("## Test Template\n\nChanges:\n")
        (tmp_path / "performance.md").write_text("## Performance Template\n\nChanges:\n")
        (tmp_path / "security.md").write_text("## Security Template\n\nChanges:\n")
        
        # Mock git commands
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="M\tsrc/main.py\nM\ttests/test_main.py\n",
                stderr=""
            )
            
            # 1. Analyze changes
            analysis_result = await analyze_file_changes("main", True)
            
            # 2. Get templates
            templates_result = await get_pr_templates()
            
            # 3. Suggest template based on analysis
            suggestion_result = await suggest_template(
                "Updated main functionality and added tests",
                "feature"
            )
            
            # Verify results
            assert all(isinstance(r, str) for r in [analysis_result, templates_result, suggestion_result])
            
            suggestion = json.loads(suggestion_result)
            assert "recommended_template" in suggestion
            assert "template_content" in suggestion
            assert suggestion["recommended_template"]["type"] == "Feature"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])