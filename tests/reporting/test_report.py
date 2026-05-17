import pytest
import os
from reporting.generator import ReportEngine
from reporting.export import ExportPipeline

@pytest.mark.asyncio
async def test_report_generation_and_export():
    engine = ReportEngine()
    states = [{"agent": "A2", "findings": []}]
    
    report = await engine.generate_report("corpus-123", states)
    assert report.overall_reliability > 0.0
    assert len(report.sections) == 2
    
    exporter = ExportPipeline()
    md_path = "test_report.md"
    docx_path = "test_report.docx"
    
    exporter.export_markdown(report, md_path)
    exporter.export_docx(report, docx_path)
    
    assert os.path.exists(md_path)
    assert os.path.exists(docx_path)
    
    # Cleanup
    os.remove(md_path)
    os.remove(docx_path)
