"""
Enhanced Report Generation utilities with PDF support
"""
import io
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import plotly.graph_objects as go
import plotly.express as px
import base64
import json
import os
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate comprehensive reports in various formats"""
    
    def __init__(self):
        self.logger = logger
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._pdf_available = self._check_pdf_availability()
    
    def _check_pdf_availability(self) -> Dict:
        """Check which PDF generation methods are available"""
        available = {
            'weasyprint': False,
            'pdfkit': False,
            'reportlab': False
        }
        
        # Check WeasyPrint - with better error handling for Windows
        try:
            import weasyprint
            available['weasyprint'] = True
            self.logger.info("WeasyPrint is available")
        except ImportError:
            self.logger.debug("WeasyPrint not installed")
        except OSError as e:
            self.logger.warning(f"WeasyPrint is installed but missing dependencies: {str(e)}")
            self.logger.warning("Install GTK from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        except Exception as e:
            self.logger.warning(f"WeasyPrint import error: {str(e)}")
        
        # Check pdfkit
        try:
            import pdfkit
            available['pdfkit'] = True
            self.logger.info("pdfkit is available")
        except ImportError:
            self.logger.debug("pdfkit not installed")
        except Exception as e:
            self.logger.warning(f"pdfkit import error: {str(e)}")
        
        # Check ReportLab
        try:
            import reportlab
            available['reportlab'] = True
            self.logger.info("ReportLab is available")
        except ImportError:
            self.logger.debug("ReportLab not installed")
        except Exception as e:
            self.logger.warning(f"ReportLab import error: {str(e)}")
        
        return available
    
    def generate_full_report(self, df: pd.DataFrame, 
                             metrics: Dict, 
                             predictions: List,
                             model_info: Dict = None,
                             figures: List[go.Figure] = None) -> Dict:
        """
        Generate a complete report with multiple sections
        
        Args:
            df: DataFrame with data
            metrics: Dictionary of metrics
            predictions: List of recent predictions
            model_info: Model performance information
            figures: List of Plotly figures to include
        
        Returns:
            Dictionary with report data and formats
        """
        report_data = {
            'timestamp': self.timestamp,
            'summary': self._generate_summary(metrics),
            'usage_analysis': self._generate_usage_analysis(df, metrics),
            'segment_analysis': self._generate_segment_analysis(df),
            'revenue_analysis': self._generate_revenue_analysis(df, metrics),
            'predictions': self._format_predictions(predictions),
            'model_performance': self._format_model_performance(model_info),
            'recommendations': self._generate_recommendations(df, metrics),
            'raw_metrics': metrics,
            'data_shape': {'rows': len(df), 'columns': len(df.columns)}
        }
        
        # Generate different formats
        formats = {
            'html': self._to_html(report_data, figures),
            'markdown': self._to_markdown(report_data),
            'json': self._to_json(report_data)
        }
        
        # Try PDF generation
        pdf_result = self._generate_pdf(report_data, figures)
        if pdf_result:
            formats['pdf'] = pdf_result
            formats['pdf_available'] = True
        else:
            formats['pdf_available'] = False
        
        return {
            'data': report_data,
            'formats': formats,
            'pdf_available': formats.get('pdf_available', False)
        }
    
    def _generate_pdf(self, report_data: Dict, figures: List[go.Figure] = None) -> Optional[bytes]:
        """Generate PDF using available library"""
        
        # Try ReportLab first (pure Python, no dependencies!)
        if self._pdf_available.get('reportlab'):
            try:
                return self._generate_pdf_reportlab(report_data)
            except Exception as e:
                self.logger.warning(f"ReportLab PDF generation failed: {str(e)}")
        
        # Try WeasyPrint second (better quality but needs GTK)
        if self._pdf_available.get('weasyprint'):
            try:
                return self._generate_pdf_weasyprint(report_data, figures)
            except Exception as e:
                self.logger.warning(f"WeasyPrint PDF generation failed: {str(e)}")
        
        # Try pdfkit third (requires wkhtmltopdf)
        if self._pdf_available.get('pdfkit'):
            try:
                return self._generate_pdf_pdfkit(report_data, figures)
            except Exception as e:
                self.logger.warning(f"pdfkit PDF generation failed: {str(e)}")
        
        return None
    
    def _generate_pdf_weasyprint(self, report_data: Dict, figures: List[go.Figure] = None) -> Optional[bytes]:
        """Generate PDF using WeasyPrint"""
        try:
            from weasyprint import HTML
            
            # Get HTML report
            html_content = self._to_html(report_data, figures)
            
            # Generate PDF
            pdf_bytes = HTML(string=html_content).write_pdf()
            self.logger.info("PDF generated successfully with WeasyPrint")
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"WeasyPrint PDF generation error: {str(e)}")
            return None
    
    def _generate_pdf_pdfkit(self, report_data: Dict, figures: List[go.Figure] = None) -> Optional[bytes]:
        """Generate PDF using pdfkit"""
        try:
            import pdfkit
            
            # Get HTML report
            html_content = self._to_html(report_data, figures)
            
            # Options for pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            # Generate PDF
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
            self.logger.info("PDF generated successfully with pdfkit")
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"pdfkit PDF generation error: {str(e)}")
            return None
    
    def _generate_pdf_reportlab(self, report_data: Dict) -> Optional[bytes]:
        """Generate PDF using ReportLab (pure Python, no dependencies)"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            styles = getSampleStyleSheet()
            
            # Add custom styles
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=0  # Center
            ))
            
            styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=12,
                spaceBefore=12
            ))
            
            styles.add(ParagraphStyle(
                name='CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leading=14
            ))
            
            styles.add(ParagraphStyle(
                name='CustomBold',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                leading=12,
                fontWeight='bold'
            ))
            
            story = []
            
            # TITLE PAGE
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("📡 Telecom Intelligence Report", styles['CustomTitle']))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("AI-Powered Consumption Analytics & Strategic Insights", styles['CustomNormal']))
            story.append(Spacer(1, 0.25*inch))
            story.append(Paragraph(f"Generated: {self.timestamp}", styles['CustomNormal']))
            story.append(Paragraph(f"Version: 3.0", styles['CustomNormal']))
            story.append(PageBreak())
            
            # EXECUTIVE SUMMARY
            summary = report_data.get('summary', {})
            story.append(Paragraph("Executive Summary", styles['CustomHeading']))
            story.append(Spacer(1, 0.1*inch))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Subscribers', f"{summary.get('total_subscribers', 0):,}"],
                ['Average Usage', f"{summary.get('avg_usage', 0):.1f} GB"],
                ['Heavy Users', f"{summary.get('pct_heavy', 0):.1f}%"],
                ['5G Adoption', f"{summary.get('pct_5g', 0):.1f}%"],
            ]
            
            if summary.get('usage_growth') is not None:
                growth = summary['usage_growth']
                summary_data.append(['Usage Growth', f"{growth:+.1f}%"])
            
            if summary.get('total_arpu'):
                summary_data.append(['Total ARPU', f"R{summary['total_arpu']:,.0f}"])
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.25*inch))
            
            # USAGE ANALYSIS
            usage = report_data.get('usage_analysis', {})
            if usage:
                story.append(Paragraph("Usage Analysis", styles['CustomHeading']))
                
                stats = usage.get('statistics', {})
                if stats:
                    story.append(Paragraph("Statistical Summary", styles['CustomBold']))
                    stats_data = [
                        ['Statistic', 'Value'],
                        ['Mean', f"{stats.get('mean', 0):.2f} GB"],
                        ['Median', f"{stats.get('median', 0):.2f} GB"],
                        ['Standard Deviation', f"{stats.get('std', 0):.2f} GB"],
                        ['Min - Max', f"{stats.get('min', 0):.2f} - {stats.get('max', 0):.2f} GB"],
                    ]
                    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(stats_table)
                    story.append(Spacer(1, 0.1*inch))
                
                dist = usage.get('distribution', {})
                if dist:
                    total = sum(dist.values()) if dist else 1
                    story.append(Paragraph("Usage Distribution", styles['CustomBold']))
                    dist_data = [
                        ['Segment', 'Count', 'Percentage'],
                        ['Low Usage (< 2 GB)', f"{dist.get('low', 0):,}", f"{(dist.get('low', 0)/total*100):.1f}%"],
                        ['Medium Usage (2-5 GB)', f"{dist.get('medium', 0):,}", f"{(dist.get('medium', 0)/total*100):.1f}%"],
                        ['High Usage (> 5 GB)', f"{dist.get('high', 0):,}", f"{(dist.get('high', 0)/total*100):.1f}%"],
                    ]
                    dist_table = Table(dist_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                    dist_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(dist_table)
                    story.append(Spacer(1, 0.1*inch))
            
            # SEGMENT ANALYSIS
            segments = report_data.get('segment_analysis', {})
            if segments:
                story.append(Paragraph("Segment Analysis", styles['CustomHeading']))
                
                plans = segments.get('plans', {})
                if plans:
                    story.append(Paragraph("Plan Type Distribution", styles['CustomBold']))
                    plan_data = [['Plan Type', 'Count', 'Percentage']]
                    for name, data in plans.items():
                        plan_data.append([name, f"{data['count']:,}", f"{data['percentage']:.1f}%"])
                    plan_table = Table(plan_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                    plan_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(plan_table)
                    story.append(Spacer(1, 0.1*inch))
                
                ages = segments.get('ages', {})
                if ages:
                    story.append(Paragraph("Age Distribution", styles['CustomBold']))
                    age_data = [['Age Group', 'Count', 'Percentage']]
                    for name, data in ages.items():
                        age_data.append([name, f"{data['count']:,}", f"{data['percentage']:.1f}%"])
                    age_table = Table(age_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                    age_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(age_table)
                    story.append(Spacer(1, 0.1*inch))
            
            # REVENUE ANALYSIS
            revenue = report_data.get('revenue_analysis', {})
            if revenue and 'arpu' in revenue:
                story.append(Paragraph("Revenue Analysis", styles['CustomHeading']))
                
                arpu = revenue['arpu']
                rev_data = [
                    ['Metric', 'Value'],
                    ['Mean ARPU', f"R{arpu.get('mean', 0):.2f}"],
                    ['Median ARPU', f"R{arpu.get('median', 0):.2f}"],
                    ['Total ARPU', f"R{arpu.get('total', 0):,.0f}"],
                ]
                if revenue.get('annual_revenue'):
                    rev_data.append(['Annual Revenue', f"R{revenue['annual_revenue']:,.0f}"])
                
                rev_table = Table(rev_data, colWidths=[2*inch, 2*inch])
                rev_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8edf3')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(rev_table)
                story.append(Spacer(1, 0.1*inch))
            
            # RECOMMENDATIONS
            recommendations = report_data.get('recommendations', [])
            if recommendations:
                story.append(PageBreak())
                story.append(Paragraph("Strategic Recommendations", styles['CustomHeading']))
                
                for i, rec in enumerate(recommendations, 1):
                    rec_text = f"""
                    <b>{i}. {rec.get('title', '')}</b><br/>
                    {rec.get('description', '')}<br/>
                    <b>Action:</b> {rec.get('action', '')}<br/>
                    <b>Priority:</b> {rec.get('priority', 'Low')} | <b>Category:</b> {rec.get('category', 'General')}
                    """
                    story.append(Paragraph(rec_text, styles['CustomNormal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # FOOTER
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("---", styles['CustomNormal']))
            story.append(Paragraph("Telecom Intelligence Report · Generated by AI-Powered Analytics Platform", styles['CustomNormal']))
            story.append(Paragraph("Data → Analysis → ML → Prediction → Business Decision", styles['CustomNormal']))
            story.append(Paragraph(f"© 2026 Telecom Intelligence · Confidential", styles['CustomNormal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            self.logger.info("PDF generated successfully with ReportLab")
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"ReportLab PDF generation error: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _generate_summary(self, metrics: Dict) -> Dict:
        """Generate executive summary"""
        return {
            'total_subscribers': metrics.get('total_subscribers', 0),
            'avg_usage': metrics.get('avg_usage', 0),
            'heavy_users': metrics.get('heavy_users', 0),
            'pct_heavy': metrics.get('pct_heavy', 0),
            'pct_5g': metrics.get('pct_5g', 0),
            'usage_growth': metrics.get('usage_growth', 0),
            'total_arpu': metrics.get('total_arpu', 0) if 'total_arpu' in metrics else None
        }
    
    def _generate_usage_analysis(self, df: pd.DataFrame, metrics: Dict) -> Dict:
        """Generate detailed usage analysis"""
        usage = {}
        
        if 'total_data_gb' in df.columns:
            data = df['total_data_gb']
            usage['statistics'] = {
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'q1': data.quantile(0.25),
                'q3': data.quantile(0.75),
                'iqr': data.quantile(0.75) - data.quantile(0.25)
            }
            
            usage['distribution'] = {
                'low': len(df[df['total_data_gb'] < 2]),
                'medium': len(df[(df['total_data_gb'] >= 2) & (df['total_data_gb'] < 5)]),
                'high': len(df[df['total_data_gb'] >= 5])
            }
        
        activity_cols = ['hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming']
        if all(col in df.columns for col in activity_cols):
            usage['activities'] = {
                'streaming': df['hours_streaming'].mean(),
                'social': df['hours_social'].mean(),
                'messaging': df['hours_messaging'].mean(),
                'gaming': df['hours_gaming'].mean()
            }
        
        return usage
    
    def _generate_segment_analysis(self, df: pd.DataFrame) -> Dict:
        """Generate segment analysis"""
        from ..constants import REV_PLAN, REV_AGE, REV_NETWORK
        
        segments = {}
        
        if 'plan_type' in df.columns:
            plan_counts = df['plan_type'].value_counts()
            segments['plans'] = {}
            for idx, count in plan_counts.items():
                name = REV_PLAN.get(idx, f'Plan_{idx}')
                segments['plans'][name] = {
                    'count': int(count),
                    'percentage': float((count / len(df)) * 100)
                }
        
        if 'age_group' in df.columns:
            age_counts = df['age_group'].value_counts()
            segments['ages'] = {}
            for idx, count in age_counts.items():
                name = REV_AGE.get(idx, f'Age_{idx}')
                segments['ages'][name] = {
                    'count': int(count),
                    'percentage': float((count / len(df)) * 100)
                }
        
        if 'network_type' in df.columns:
            network_counts = df['network_type'].value_counts()
            segments['networks'] = {}
            for idx, count in network_counts.items():
                name = REV_NETWORK.get(idx, f'Network_{idx}')
                segments['networks'][name] = {
                    'count': int(count),
                    'percentage': float((count / len(df)) * 100)
                }
        
        return segments
    
    def _generate_revenue_analysis(self, df: pd.DataFrame, metrics: Dict) -> Dict:
        """Generate revenue analysis"""
        from ..models.manager import ModelMetrics
        
        revenue = {}
        
        if 'plan_type' in df.columns and 'total_data_gb' in df.columns:
            try:
                df_arpu = df.copy()
                df_arpu['arpu'] = df_arpu.apply(
                    lambda row: ModelMetrics.calculate_arpu(row['total_data_gb'], row['plan_type']),
                    axis=1
                )
                
                revenue['arpu'] = {
                    'mean': float(df_arpu['arpu'].mean()),
                    'median': float(df_arpu['arpu'].median()),
                    'total': float(df_arpu['arpu'].sum()),
                    'std': float(df_arpu['arpu'].std())
                }
                
                arpu_by_plan = df_arpu.groupby('plan_type')['arpu'].mean()
                from ..constants import REV_PLAN
                revenue['arpu_by_plan'] = {}
                for idx, value in arpu_by_plan.items():
                    name = REV_PLAN.get(idx, f'Plan_{idx}')
                    revenue['arpu_by_plan'][name] = float(value)
                
                revenue['annual_revenue'] = float(df_arpu['arpu'].sum() * 12)
                
            except Exception as e:
                self.logger.error(f"Error calculating revenue: {str(e)}")
        
        return revenue
    
    def _format_predictions(self, predictions: List) -> List:
        """Format predictions for report"""
        formatted = []
        for pred in predictions[-20:]:
            formatted.append({
                'timestamp': pred.get('timestamp', ''),
                'plan_type': pred.get('plan_type', ''),
                'device_type': pred.get('device_type', ''),
                'age_group': pred.get('age_group', ''),
                'network_type': pred.get('network_type', ''),
                'prediction': float(pred.get('prediction', 0)),
                'arpu_zar': float(pred.get('arpu_zar', 0))
            })
        return formatted
    
    def _format_model_performance(self, model_info: Dict) -> Dict:
        """Format model performance metrics"""
        if not model_info:
            return {}
        
        perf = model_info.get('performance', {})
        return {
            'r2_score': perf.get('r2_score', 'N/A'),
            'train_r2_score': perf.get('train_r2_score', 'N/A'),
            'rmse': perf.get('rmse', 'N/A'),
            'mae': perf.get('mae', 'N/A'),
            'training_samples': perf.get('training_samples', 'N/A'),
            'test_samples': perf.get('test_samples', 'N/A'),
            'is_real': model_info.get('is_real', False)
        }
    
    def _generate_recommendations(self, df: pd.DataFrame, metrics: Dict) -> List:
        """Generate actionable recommendations"""
        recommendations = []
        
        heavy_pct = metrics.get('pct_heavy', 0)
        if heavy_pct > 20:
            recommendations.append({
                'priority': 'High',
                'category': 'Revenue',
                'title': 'Premium Bundle Upsell',
                'description': f"{heavy_pct:.1f}% of users are heavy users. Target them with premium bundles to increase ARPU.",
                'action': 'Launch targeted campaign for heavy users'
            })
        
        pct_5g = metrics.get('pct_5g', 0)
        if pct_5g > 10:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Network',
                'title': '5G Expansion Opportunity',
                'description': f"{pct_5g:.1f}% of users are on 5G. Consider expanding 5G coverage.",
                'action': 'Invest in 5G infrastructure'
            })
        
        growth = metrics.get('usage_growth', 0)
        if growth < 0:
            recommendations.append({
                'priority': 'High',
                'category': 'Retention',
                'title': 'Usage Decline Detected',
                'description': f"Usage has declined by {abs(growth):.1f}%. Investigate potential churn indicators.",
                'action': 'Launch engagement campaigns'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'Low',
                'category': 'General',
                'title': 'Monitor Performance',
                'description': 'All metrics are within normal ranges. Continue monitoring.',
                'action': 'Regular monitoring'
            })
        
        return recommendations
    
    def _to_html(self, report_data: Dict, figures: List[go.Figure] = None) -> str:
        """Convert report data to HTML"""
        summary = report_data.get('summary', {})
        recommendations = report_data.get('recommendations', [])
        data_shape = report_data.get('data_shape', {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Telecom Intelligence Report</title>
            <meta charset="UTF-8">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f8fafc;
                    color: #0f172a;
                    padding: 40px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .report-header {{
                    background: linear-gradient(135deg, #0f172a 0%, #1a237e 30%, #3949ab 60%, #5c6bc0 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 24px;
                    margin-bottom: 30px;
                    box-shadow: 0 8px 32px rgba(26, 35, 126, 0.2);
                }}
                .report-header h1 {{ font-size: 2.5rem; font-weight: 800; letter-spacing: -0.02em; }}
                .report-header .subtitle {{ font-size: 1.1rem; opacity: 0.8; margin-top: 8px; }}
                .report-header .meta {{
                    margin-top: 16px;
                    display: flex;
                    gap: 20px;
                    font-size: 0.9rem;
                    opacity: 0.7;
                }}
                .card {{
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    margin-bottom: 24px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
                    border: 1px solid #e8edf3;
                }}
                .card h2 {{ font-size: 1.3rem; font-weight: 700; color: #0f172a; margin-bottom: 16px; }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 20px;
                }}
                .metric-box {{
                    background: #f8fafc;
                    padding: 16px;
                    border-radius: 12px;
                    text-align: center;
                    border: 1px solid #e8edf3;
                }}
                .metric-box .value {{ font-size: 2rem; font-weight: 800; color: #1a237e; }}
                .metric-box .label {{ font-size: 0.8rem; color: #64748b; margin-top: 4px; }}
                .recommendation {{
                    padding: 16px;
                    border-radius: 12px;
                    margin-bottom: 12px;
                    border-left: 4px solid;
                }}
                .recommendation.high {{ background: #fef2f2; border-left-color: #dc2626; }}
                .recommendation.medium {{ background: #fffbeb; border-left-color: #d97706; }}
                .recommendation.low {{ background: #f0fdf4; border-left-color: #16a34a; }}
                .recommendation .title {{ font-weight: 600; font-size: 1rem; }}
                .recommendation .desc {{ color: #64748b; font-size: 0.9rem; margin: 4px 0; }}
                .recommendation .action {{ color: #1a237e; font-size: 0.85rem; font-weight: 500; }}
                .report-footer {{
                    text-align: center;
                    padding: 24px;
                    color: #94a3b8;
                    font-size: 0.8rem;
                    border-top: 1px solid #e8edf3;
                    margin-top: 24px;
                }}
                @media (max-width: 768px) {{
                    body {{ padding: 16px; }}
                    .report-header {{ padding: 24px; }}
                    .report-header h1 {{ font-size: 1.8rem; }}
                    .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                }}
            </style>
        </head>
        <body>
            <div class="report-header">
                <h1>📡 Telecom Intelligence Report</h1>
                <div class="subtitle">AI-Powered Consumption Analytics & Strategic Insights</div>
                <div class="meta">
                    <span>📅 Generated: {self.timestamp}</span>
                    <span>📊 Version: 3.0</span>
                    <span>📁 {data_shape.get('rows', 0):,} rows · {data_shape.get('columns', 0)} columns</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="value">{summary.get('total_subscribers', 0):,}</div>
                        <div class="label">👥 Total Subscribers</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">{summary.get('avg_usage', 0):.1f} GB</div>
                        <div class="label">📊 Average Usage</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">{summary.get('pct_heavy', 0):.1f}%</div>
                        <div class="label">🔥 Heavy Users</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">{summary.get('pct_5g', 0):.1f}%</div>
                        <div class="label">📡 5G Adoption</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>💡 Strategic Recommendations</h2>
        """
        
        for rec in recommendations[:3]:
            priority_class = rec.get('priority', 'low').lower()
            html += f"""
                <div class="recommendation {priority_class}">
                    <div class="title">🔄 {rec['title']}</div>
                    <div class="desc">{rec['description']}</div>
                    <div class="action">💡 Action: {rec['action']}</div>
                    <div style="margin-top: 4px; font-size: 0.8rem; color: #94a3b8;">
                        {rec['priority']} Priority · {rec['category']}
                    </div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="report-footer">
                <strong>Telecom Intelligence Report</strong> · Generated by AI-Powered Analytics Platform
                <br>
                <span style="color: #94a3b8;">Data → Analysis → ML → Prediction → Business Decision</span>
                <br>
                <span style="color: #94a3b8; font-size: 0.75rem;">© 2026 Telecom Intelligence · Confidential</span>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _to_markdown(self, report_data: Dict) -> str:
        """Convert report data to Markdown"""
        lines = []
        
        lines.append("# 📡 Telecom Intelligence Report")
        lines.append(f"*Generated: {self.timestamp}*\n")
        
        summary = report_data.get('summary', {})
        lines.append("## 📊 Executive Summary")
        lines.append(f"- **Total Subscribers:** {summary.get('total_subscribers', 0):,}")
        lines.append(f"- **Average Usage:** {summary.get('avg_usage', 0):.1f} GB")
        lines.append(f"- **Heavy Users:** {summary.get('pct_heavy', 0):.1f}%")
        lines.append(f"- **5G Adoption:** {summary.get('pct_5g', 0):.1f}%\n")
        
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            lines.append("## 💡 Strategic Recommendations")
            for rec in recommendations[:3]:
                lines.append(f"### 🔄 {rec['title']}")
                lines.append(f"- {rec['description']}")
                lines.append(f"- **Action:** {rec['action']}")
                lines.append(f"- **Priority:** {rec['priority']} | **Category:** {rec['category']}\n")
        
        lines.append("\n---")
        lines.append(f"*Report generated by Telecom Intelligence Platform v3.0*")
        
        return "\n".join(lines)
    
    def _to_json(self, report_data: Dict) -> str:
        """Convert report data to JSON"""
        return json.dumps(report_data, indent=2, default=str)