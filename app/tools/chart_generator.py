import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import base64
from io import BytesIO


def generate_chart(data, chart_type):
    """Generate a chart from financial data
    
    Args:
        data: List of values or list of lists for comparison
        chart_type: 'line', 'bar', or 'comparison'
    
    Returns:
        Base64 encoded PNG image string
    """
    try:
        fig = plt.figure(figsize=(10, 6))
        
        if chart_type == "line":
            if not data:
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                plt.plot(data, marker='o', linewidth=2)
                plt.title("Financial Trend")
                plt.xlabel("Period")
                plt.ylabel("Value")
                plt.grid(True, alpha=0.3)

        elif chart_type == "bar":
            if not data:
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                plt.bar(range(len(data)), data)
                plt.title("Financial Metrics")
                plt.xlabel("Index")
                plt.ylabel("Value")
                plt.grid(True, alpha=0.3, axis='y')

        elif chart_type == "comparison":
            if not data or all(len(series) == 0 for series in data):
                plt.text(0.5, 0.5, "No data available", ha='center', va='center')
            else:
                labels = ["Revenue", "Profit"]
                for idx, series in enumerate(data):
                    if series:
                        plt.plot(series, marker='o', label=labels[idx] if idx < len(labels) else f"Series {idx}")
                plt.title("Financial Comparison")
                plt.xlabel("Period")
                plt.ylabel("Value")
                plt.legend()
                plt.grid(True, alpha=0.3)

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
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error generating chart: {str(e)}", ha='center', va='center')
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return chart_base64