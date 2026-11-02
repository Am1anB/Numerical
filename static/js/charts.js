function formatNumber(value) {
  if (typeof value !== "number") {
    return value ?? "-";
  }
  if (value === 0) {
    return "0";
  }
  const size = Math.abs(value);
  if (size >= 1e7 || size < 1e-3) {
    return value.toExponential(6);
  }
  return String(Number(value.toPrecision(10)));
}

class ChartDrawer {
  constructor(container) {
    this.container = container;
    this.charts = [];

    const styles = getComputedStyle(document.documentElement);
    this.surface = styles.getPropertyValue("--surface").trim();
    this.textColor = styles.getPropertyValue("--text-secondary").trim();
    this.gridColor = styles.getPropertyValue("--grid").trim();
    this.axisColor = styles.getPropertyValue("--baseline").trim();
    this.blue = styles.getPropertyValue("--series-1").trim();
    this.orange = styles.getPropertyValue("--series-2").trim();
    this.green = styles.getPropertyValue("--series-3").trim();
  }

  clear() {
    this.charts.forEach((chart) => chart.destroy());
    this.charts = [];
  }

  draw(chart) {
    if (chart.type === "root") {
      this.drawRootChart(chart);
      if (chart.errors.length > 1) {
        this.drawErrorChart(chart);
      }
    } else if (chart.type === "lines") {
      this.drawLinesChart(chart);
    } else {
      this.drawBarChart(chart);
    }
  }

  addCanvas(title, note) {
    const panel = document.createElement("section");
    panel.className = "panel";

    const heading = document.createElement("h2");
    heading.textContent = title;
    panel.append(heading);

    if (note) {
      const noteElement = document.createElement("p");
      noteElement.className = "chart-note";
      noteElement.textContent = note;
      panel.append(noteElement);
    }

    const box = document.createElement("div");
    box.className = "chart-box";
    const canvas = document.createElement("canvas");
    box.append(canvas);
    panel.append(box);

    this.container.append(panel);
    return canvas;
  }

  axis(title, extra = {}) {
    return {
      title: { display: Boolean(title), text: title, color: this.textColor },
      ticks: { color: this.textColor },
      border: { color: this.axisColor },
      grid: { color: (context) => (context.tick?.value === 0 ? this.axisColor : this.gridColor) },
      ...extra,
    };
  }

  options(scales, showLegend) {
    return {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "nearest", intersect: false },
      scales: scales,
      plugins: {
        legend: {
          display: showLegend,
          align: "start",
          labels: { color: this.textColor, usePointStyle: true },
        },
      },
    };
  }

  lineData(label, points, color) {
    return {
      label: label,
      data: points,
      showLine: true,
      borderColor: color,
      backgroundColor: color,
      borderWidth: 2,
      pointRadius: 0,
      pointHitRadius: 10,
      pointStyle: "line",
    };
  }

  pointData(label, points, color, style, radius) {
    return {
      label: label,
      data: points,
      backgroundColor: color,
      borderColor: this.surface,
      borderWidth: 2,
      pointStyle: style,
      pointRadius: radius,
      pointHoverRadius: radius + 1,
    };
  }

  /* Finds the y range to show, ignoring huge spikes like the ones in tan(x). */
  visibleRange(curve) {
    const ys = curve.map((point) => point.y).filter((y) => y !== null).sort((a, b) => a - b);
    if (ys.length === 0) {
      return [-1, 1];
    }

    let low = ys[0];
    let high = ys[ys.length - 1];
    const middleLow = ys[Math.floor(ys.length * 0.05)];
    const middleHigh = ys[Math.ceil(ys.length * 0.95) - 1];
    if (high - low > 5 * (middleHigh - middleLow)) {
      low = middleLow;
      high = middleHigh;
    }

    low = Math.min(low, 0);
    high = Math.max(high, 0);
    const padding = (high - low || 1) * 0.08;
    return [low - padding, high + padding];
  }

  drawRootChart(chart) {
    const [yMin, yMax] = this.visibleRange(chart.curve);

    // Leave a gap in the line where the value is far off the graph.
    const limit = 2 * (yMax - yMin);
    const curve = chart.curve.map((point) => {
      const tooFar = point.y === null || point.y < yMin - limit || point.y > yMax + limit;
      return { x: point.x, y: tooFar ? null : point.y };
    });

    const datasets = [
      this.lineData("f(x)", curve, this.blue),
      this.pointData("Iterations", chart.iterations, this.orange, "circle", 6),
    ];
    if (chart.root) {
      const label = "Root: x = " + formatNumber(Number(chart.root.x.toPrecision(6)));
      datasets.push(this.pointData(label, [chart.root], this.green, "rectRot", 8));
    }

    const scales = {
      x: this.axis("x", { type: "linear", min: chart.low, max: chart.high }),
      y: this.axis("f(x)", { min: yMin, max: yMax }),
    };
    const canvas = this.addCanvas(chart.title, "The dots show the estimate from each iteration.");
    this.charts.push(new Chart(canvas, { type: "scatter", data: { datasets }, options: this.options(scales, true) }));
  }

  drawErrorChart(chart) {
    const dataset = this.lineData("Error", chart.errors, this.blue);
    dataset.pointRadius = 4;
    dataset.pointStyle = "circle";

    const scales = {
      x: this.axis("Iteration", { type: "linear", ticks: { color: this.textColor, precision: 0 } }),
      y: this.axis("Error", {
        type: "logarithmic",
        ticks: {
          color: this.textColor,
          maxTicksLimit: 8,
          callback: (value) => Number(value.toPrecision(2)).toExponential(),
        },
      }),
    };
    const canvas = this.addCanvas("Error at each iteration", "Log scale. A falling line means the method is converging.");
    this.charts.push(new Chart(canvas, { type: "scatter", data: { datasets: [dataset] }, options: this.options(scales, false) }));
  }

  drawBarChart(chart) {
    const dataset = {
      label: "Value",
      data: chart.values,
      backgroundColor: this.blue,
      maxBarThickness: 24,
      borderRadius: 4,
      borderSkipped: "start",
    };
    const labels = chart.values.map((value, index) => "x" + (index + 1));
    const scales = { x: this.axis(""), y: this.axis("Value", { grace: "10%" }) };
    const canvas = this.addCanvas(chart.title);
    this.charts.push(new Chart(canvas, { type: "bar", data: { labels, datasets: [dataset] }, options: this.options(scales, false) }));
  }

  drawLinesChart(chart) {
    const answer = `Solution: (${formatNumber(chart.solution.x)}, ${formatNumber(chart.solution.y)})`;
    const datasets = [
      this.lineData(chart.lines[0].label, chart.lines[0].points, this.blue),
      this.lineData(chart.lines[1].label, chart.lines[1].points, this.orange),
      this.pointData(answer, [chart.solution], this.green, "rectRot", 8),
    ];
    const ticks = { color: this.textColor, callback: (value) => Number(value.toPrecision(4)) };
    const scales = {
      x: this.axis("x1", { type: "linear", min: chart.x_low, max: chart.x_high, ticks }),
      y: this.axis("x2", { min: chart.y_low, max: chart.y_high, ticks }),
    };
    const canvas = this.addCanvas(chart.title);
    this.charts.push(new Chart(canvas, { type: "scatter", data: { datasets }, options: this.options(scales, true) }));
  }
}
