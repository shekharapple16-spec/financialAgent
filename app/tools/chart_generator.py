import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import base64
from io import BytesIO


def generate_chart(data, chart_type):
    """Generate a chart from financial data
    
    Args:
        data: List of values or list of lists for comparison
        chart_type: 'line', 'bar', 'comparison', or 'none'
    
    Returns:
        Base64 encoded PNG image string
    """
    try:
        fig = plt.figure(figsize=(12, 7))
        
        if chart_type == "line":
            if not data:
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                # Filter out None and empty values
                data = [x for x in data if x is not None and isinstance(x, (int, float))]
                if data:
                    plt.plot(data, marker='o', linewidth=2.5, markersize=8, color='#1f77b4')
                    plt.title("Financial Trend Analysis", fontsize=14, fontweight='bold')
                    plt.xlabel("Period", fontsize=12)
                    plt.ylabel("Value", fontsize=12)
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                else:
                    plt.text(0.5, 0.5, "No valid numeric data", ha='center', va='center')

        elif chart_type == "bar":
            if not data:
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                # Filter out None and empty values
                data = [x for x in data if x is not None and isinstance(x, (int, float))]
                if data:
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    bar_colors = [colors[i % len(colors)] for i in range(len(data))]
                    plt.bar(range(len(data)), data, color=bar_colors)
                    plt.title("Financial Metrics", fontsize=14, fontweight='bold')
                    plt.xlabel("Metric", fontsize=12)
                    plt.ylabel("Value", fontsize=12)
                    plt.grid(True, alpha=0.3, axis='y')
                    plt.tight_layout()
                else:
                    plt.text(0.5, 0.5, "No valid numeric data", ha='center', va='center')

        elif chart_type == "comparison":
            if not data or all(not series for series in data):
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                # Handle comparison data [revenue_data, profit_data]
                labels = ["Revenue", "Profit", "Income", "Expenses", "Margins"]
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                
                for idx, series in enumerate(data):
                    if series:
                        # Filter out None and empty values
                        series = [x for x in series if x is not None and isinstance(x, (int, float))]
                        if series:
                            label = labels[idx] if idx < len(labels) else f"Series {idx}"
                            color = colors[idx] if idx < len(colors) else None
                            plt.plot(series, marker='o', label=label, linewidth=2.5, markersize=8, color=color)
                
                plt.title("Financial Comparison", fontsize=14, fontweight='bold')
                plt.xlabel("Period", fontsize=12)
                plt.ylabel("Value", fontsize=12)
                plt.legend(loc='best', fontsize=10)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
        
        else:  # chart_type == "none" or unknown
            plt.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12)

        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches='tight')
        buffer.seek(0)

        # Encode to base64
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)

        return chart_base64
    
    except Exception as e:
        # Return error image
        plt.figure(figsize=(12, 7))
        plt.text(0.5, 0.5, f"Error generating chart: {str(e)}", ha='center', va='center')
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return chart_base64