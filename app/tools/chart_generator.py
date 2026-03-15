import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def generate_chart(data, chart_type, title="Financial Analysis"):
    """Generate professional financial charts from data
    
    Args:
        data: Chart data (format depends on chart_type)
        chart_type: 'line', 'bar', 'grouped_bar', 'comparison', or 'none'
        title: Chart title
    
    Returns:
        Base64 encoded PNG image string
    """
    try:
        fig = plt.figure(figsize=(14, 8))
        fig.patch.set_facecolor('#f5f5f5')
        
        if chart_type == "line":
            _generate_line_chart(data, title)
        
        elif chart_type == "bar":
            _generate_bar_chart(data, title)
        
        elif chart_type == "grouped_bar":
            _generate_grouped_bar_chart(data, title)
        
        elif chart_type == "comparison":
            _generate_comparison_chart(data, title)
        
        else:  # chart_type == "none" or unknown
            plt.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12)

        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=120, bbox_inches='tight', facecolor='#f5f5f5')
        buffer.seek(0)

        # Encode to base64
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)

        return chart_base64
    
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}", exc_info=True)
        # Return error image
        fig = plt.figure(figsize=(14, 8))
        plt.text(0.5, 0.5, f"Error generating chart: {str(e)}", ha='center', va='center')
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=120)
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return chart_base64


def _generate_line_chart(data, title):
    """Generate a line chart for trend analysis"""
    if not data:
        plt.text(0.5, 0.5, "No data available", ha='center', va='center')
        return
    
    # Filter numeric values
    data = [x for x in data if x is not None and isinstance(x, (int, float))]
    if not data:
        plt.text(0.5, 0.5, "No valid numeric data", ha='center', va='center')
        return
    
    ax = plt.gca()
    ax.set_facecolor('white')
    
    plt.plot(range(len(data)), data, marker='o', linewidth=3, markersize=10, 
             color='#2E86AB', markerfacecolor='#A23B72', markeredgewidth=2)
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Period", fontsize=12, fontweight='bold')
    plt.ylabel("Amount (Cr)", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()


def _generate_bar_chart(data, title):
    """Generate a bar chart for metric comparison"""
    if not data:
        plt.text(0.5, 0.5, "No data available", ha='center', va='center')
        return
    
    # Filter numeric values
    data = [x for x in data if x is not None and isinstance(x, (int, float))]
    if not data:
        plt.text(0.5, 0.5, "No valid numeric data", ha='center', va='center')
        return
    
    ax = plt.gca()
    ax.set_facecolor('white')
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    bar_colors = [colors[i % len(colors)] for i in range(len(data))]
    
    bars = plt.bar(range(len(data)), data, color=bar_colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, data)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'{val:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Metric", fontsize=12, fontweight='bold')
    plt.ylabel("Amount (Cr)", fontsize=12, fontweight='bold')
    plt.xticks(range(len(data)), [f'Metric {i+1}' for i in range(len(data))], fontsize=10)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()


def _generate_grouped_bar_chart(data, title):
    """Generate grouped bar chart for year-over-year comparison
    
    Args:
        data: Dict with structure {
            'categories': ['Revenue', 'Profit', ...],
            'current_year': [val1, val2, ...],
            'prior_year': [val3, val4, ...],
            'labels': ['FY14', 'FY13']
        }
    """
    if not data or not isinstance(data, dict):
        plt.text(0.5, 0.5, "No data available", ha='center', va='center')
        return
    
    categories = data.get('categories', [])
    current = data.get('current_year', [])
    prior = data.get('prior_year', [])
    labels = data.get('labels', ['Current', 'Prior'])
    
    if not categories or (not current and not prior):
        plt.text(0.5, 0.5, "No valid data for comparison", ha='center', va='center')
        return
    
    ax = plt.gca()
    ax.set_facecolor('white')
    
    x = np.arange(len(categories))
    width = 0.35
    
    colors = ['#2E86AB', '#A7C957']
    
    # Plot bars
    if current:
        current = [v if isinstance(v, (int, float)) else 0 for v in current]
        bars1 = plt.bar(x - width/2, current, width, label=labels[0], 
                       color=colors[0], edgecolor='black', linewidth=1.5)
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    if prior:
        prior = [v if isinstance(v, (int, float)) else 0 for v in prior]
        bars2 = plt.bar(x + width/2, prior, width, label=labels[1], 
                       color=colors[1], edgecolor='black', linewidth=1.5)
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Revenue Categories", fontsize=12, fontweight='bold')
    plt.ylabel("Amount (Cr)", fontsize=12, fontweight='bold')
    plt.xticks(x, categories, fontsize=11, fontweight='bold')
    plt.legend(loc='upper left', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()


def _generate_comparison_chart(data, title):
    """Generate comparison chart for multiple metrics"""
    if not data or not isinstance(data, dict):
        plt.text(0.5, 0.5, "No data available", ha='center', va='center')
        return
    
    ax = plt.gca()
    ax.set_facecolor('white')
    
    # Handle dict-based comparison data
    if 'series' in data:
        series_data = data['series']
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        for idx, (name, values) in enumerate(series_data.items()):
            if values:
                values = [v if isinstance(v, (int, float)) else 0 for v in values]
                plt.plot(range(len(values)), values, marker='o', label=name, 
                        linewidth=2.5, markersize=8, color=colors[idx % len(colors)])
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Period", fontsize=12, fontweight='bold')
    plt.ylabel("Amount (Cr)", fontsize=12, fontweight='bold')
    plt.legend(loc='best', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()