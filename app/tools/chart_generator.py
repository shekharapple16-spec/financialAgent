import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import base64
from io import BytesIO


def generate_chart(data, chart_type):

    plt.figure()

    if chart_type == "line":
        plt.plot(data)

    if chart_type == "bar":
        plt.bar(range(len(data)), data)

    if chart_type == "comparison":
        for series in data:
            plt.plot(series)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    chart_base64 = base64.b64encode(buffer.read()).decode()

    plt.close()

    return chart_base64