"""
Report generation utilities
"""
import io
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate reports in various formats"""
    
    def __init__(self):
        self.logger = logger
    
    def generate_markdown_report(self, df: pd.DataFrame, 
                                  metrics: Dict, 
                                  predictions: List) -> str:
        """Generate a Markdown report"""
        report = []
        
        # Header
        report.append("# Telecom Consumption Intelligence Report")
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Total Subscribers:** {metrics.get('total_subscribers', 0):,}")
        report.append(f"- **Average Usage:** {metrics.get('avg_usage', 0):.2f} GB")
        report.append(f"- **Heavy Users:** {metrics.get('heavy_users', 0):,} ({metrics.get('pct_heavy', 0):.1f}%)")
        report.append(f"- **5G Adoption:** {metrics.get('pct_5g', 0):.1f}%\n")
        
        # Usage Statistics
        report.append("## 📈 Usage Statistics")
        report.append(f"- **Min Usage:** {metrics.get('min_usage', 0):.2f} GB")
        report.append(f"- **Max Usage:** {metrics.get('max_usage', 0):.2f} GB")
        report.append(f"- **Median Usage:** {metrics.get('median_usage', 0):.2f} GB")
        report.append(f"- **Std Deviation:** {metrics.get('std_usage', 0):.2f} GB\n")
        
        # Predictions
        if predictions:
            report.append("## 🎯 Recent Predictions")
            for pred in predictions[-5:]:
                report.append(f"- {pred.get('timestamp', '')} - {pred.get('plan_type', '')}: {pred.get('prediction', 0):.2f} GB (ARPU: R{pred.get('arpu_zar', 0):.2f})")
        
        # Recommendations
        report.append("\n## 💡 Recommendations")
        heavy_users = metrics.get('heavy_users', 0)
        if heavy_users > 0:
            report.append(f"- Target {heavy_users:,} heavy users for premium bundles")
        if metrics.get('pct_5g', 0) > 0:
            report.append(f"- {metrics.get('pct_5g', 0):.1f}% of users on 5G - consider expanding 5G coverage")
        
        return "\n".join(report)
    
    def generate_html_report(self, df: pd.DataFrame, 
                             metrics: Dict, 
                             predictions: List,
                             figures: List[go.Figure] = None) -> str:
        """Generate an HTML report with charts"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Telecom Consumption Report</title>
            <style>
                body {{ font-family: 'Inter', sans-serif; margin: 40px; background: #f8fafc; }}
                .header {{ background: linear-gradient(135deg, #1a237e, #3949ab); color: white; padding: 30px; border-radius: 16px; }}
                .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #1a237e; }}
                .metric-label {{ color: #64748b; font-size: 0.8em; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #e8edf3; }}
                th {{ background: #f1f5f9; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📡 Telecom Consumption Intelligence Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Summary</h2>
                <div class="metric">
                    <div class="metric-value">{metrics.get('total_subscribers', 0):,}</div>
                    <div class="metric-label">Total Subscribers</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{metrics.get('avg_usage', 0):.2f} GB</div>
                    <div class="metric-label">Average Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{metrics.get('pct_heavy', 0):.1f}%</div>
                    <div class="metric-label">Heavy Users</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{metrics.get('pct_5g', 0):.1f}%</div>
                    <div class="metric-label">5G Adoption</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Usage Statistics</h2>
                <table>
                    <tr>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Median</th>
                        <th>Std Dev</th>
                    </tr>
                    <tr>
                        <td>{metrics.get('min_usage', 0):.2f} GB</td>
                        <td>{metrics.get('max_usage', 0):.2f} GB</td>
                        <td>{metrics.get('median_usage', 0):.2f} GB</td>
                        <td>{metrics.get('std_usage', 0):.2f} GB</td>
                    </tr>
                </table>
            </div>
        """
        
        # Add predictions section
        if predictions:
            html += """
            <div class="section">
                <h2>🎯 Recent Predictions</h2>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Plan</th>
                        <th>Prediction (GB)</th>
                        <th>ARPU (ZAR)</th>
                    </tr>
            """
            for pred in predictions[-10:]:
                html += f"""
                    <tr>
                        <td>{pred.get('timestamp', '')}</td>
                        <td>{pred.get('plan_type', '')}</td>
                        <td>{pred.get('prediction', 0):.2f}</td>
                        <td>R{pred.get('arpu_zar', 0):.2f}</td>
                    </tr>
                """
            html += "</table></div>"
        
        html += """
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul>
        """
        
        heavy_users = metrics.get('heavy_users', 0)
        if heavy_users > 0:
            html += f"<li>Target {heavy_users:,} heavy users for premium bundles</li>"
        if metrics.get('pct_5g', 0) > 0:
            html += f"<li>{metrics.get('pct_5g', 0):.1f}% of users on 5G - consider expanding 5G coverage</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def export_to_pdf(self, html_content: str, filename: str = None) -> bytes:
        """Convert HTML to PDF (requires weasyprint or similar)"""
        try:
            from weasyprint import HTML
            import tempfile
            
            if filename is None:
                filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create PDF from HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
            
        except ImportError:
            self.logger.warning("WeasyPrint not installed. Install with: pip install weasyprint")
            return None
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            return None