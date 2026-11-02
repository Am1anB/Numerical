class MethodPage {
  constructor() {
    this.api = new Api();
    this.form = document.getElementById("method-form");
    this.results = document.getElementById("results");
    this.history = document.getElementById("history");
    this.slug = this.form.dataset.slug;
    this.kind = this.form.dataset.kind;
    this.chartDrawer = new ChartDrawer(this.results);

    if (this.kind === "matrix") {
      this.sizeSelect = document.getElementById("matrix-size");
      this.grid = document.getElementById("matrix-grid");
      this.sizeSelect.addEventListener("change", () => this.resizeMatrix());
      this.fillMatrix(JSON.parse(this.grid.dataset.default));
    }

    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.calculate();
    });

    this.loadHistory();
  }

  // Reading and filling the form

  readInputs() {
    if (this.kind === "matrix") {
      return { system: this.readMatrix() };
    }
    const inputs = {};
    for (const input of this.form.querySelectorAll("input")) {
      inputs[input.name] = input.value.trim();
    }
    return inputs;
  }

  fillInputs(inputs) {
    if (this.kind === "matrix") {
      this.fillMatrix(inputs.system);
      return;
    }
    for (const input of this.form.querySelectorAll("input")) {
      input.value = inputs[input.name];
    }
  }

  // Matrix grid

  fillMatrix(system) {
    const size = system.b.length;
    this.sizeSelect.value = size;
    this.grid.style.setProperty("--size", size);
    this.grid.replaceChildren();

    for (let j = 1; j <= size; j++) {
      this.grid.append(this.matrixHeading("x" + j));
    }
    this.grid.append(this.matrixHeading("b"));

    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        this.grid.append(this.matrixCell(`A${i}${j}`, system.A[i][j], `A row ${i + 1} column ${j + 1}`));
      }
      const cell = this.matrixCell(`b${i}`, system.b[i], `b row ${i + 1}`);
      cell.classList.add("constant");
      this.grid.append(cell);
    }
  }

  matrixHeading(text) {
    const heading = document.createElement("span");
    heading.className = "matrix-heading";
    heading.textContent = text;
    return heading;
  }

  matrixCell(name, value, label) {
    const input = document.createElement("input");
    input.className = "mono";
    input.name = name;
    input.value = value;
    input.autocomplete = "off";
    input.setAttribute("aria-label", label);
    return input;
  }

  readMatrix() {
    const size = this.grid.querySelectorAll("input.constant").length;
    const cell = (name) => this.grid.querySelector(`input[name=${name}]`).value.trim();

    const A = [];
    const b = [];
    for (let i = 0; i < size; i++) {
      const row = [];
      for (let j = 0; j < size; j++) {
        row.push(cell(`A${i}${j}`));
      }
      A.push(row);
      b.push(cell(`b${i}`));
    }
    return { A, b };
  }

  resizeMatrix() {
    const oldSystem = this.readMatrix();
    const size = Number(this.sizeSelect.value);

    const A = [];
    const b = [];
    for (let i = 0; i < size; i++) {
      const row = [];
      for (let j = 0; j < size; j++) {
        row.push(oldSystem.A[i]?.[j] ?? "");
      }
      A.push(row);
      b.push(oldSystem.b[i] ?? "");
    }
    this.fillMatrix({ A, b });
  }

  // Calculating

  async calculate() {
    this.results.classList.add("is-loading");
    try {
      const calculation = await this.api.calculate(this.slug, this.readInputs());
      this.showResult(calculation.result);
      await this.loadHistory();
    } catch (error) {
      this.showError(error.message);
    }
  }

  // Showing results

  showResult(result) {
    this.clearResults();

    if (result.warning) {
      this.addNotice("Warning: " + result.warning, "notice-warning");
    }
    this.addAnswers(result.answers);
    this.chartDrawer.draw(result.chart);
    this.addTable(result.table);
    if (result.steps.length > 0) {
      this.addSteps(result.steps);
    }
  }

  showError(message) {
    this.clearResults();
    this.addNotice("Error: " + message, "notice-error");
  }

  clearResults() {
    this.chartDrawer.clear();
    this.results.replaceChildren();
    this.results.classList.remove("is-loading");
  }

  addNotice(message, className) {
    const notice = document.createElement("p");
    notice.className = "notice " + className;
    notice.setAttribute("role", "alert");
    notice.textContent = message;
    this.results.append(notice);
  }

  addAnswers(answers) {
    const box = document.createElement("div");
    box.className = "answers";

    for (const answer of answers) {
      const card = document.createElement("div");
      card.className = "answer";

      const label = document.createElement("span");
      label.className = "answer-label";
      label.textContent = answer.label;

      const value = document.createElement("span");
      value.className = "answer-value";
      value.textContent = formatNumber(answer.value);

      card.append(label, value);
      box.append(card);
    }
    this.results.append(box);
  }

  addTable(table) {
    const headerRow = document.createElement("tr");
    for (const column of table.columns) {
      const cell = document.createElement("th");
      cell.scope = "col";
      cell.textContent = column.label;
      headerRow.append(cell);
    }

    const head = document.createElement("thead");
    head.append(headerRow);

    const body = document.createElement("tbody");
    for (const row of table.rows) {
      const tableRow = document.createElement("tr");
      for (const column of table.columns) {
        const cell = document.createElement("td");
        cell.textContent = formatNumber(row[column.key]);
        tableRow.append(cell);
      }
      body.append(tableRow);
    }

    const element = document.createElement("table");
    element.className = "data-table";
    element.append(head, body);
    this.addPanel(table.title, this.scrollBox(element));
  }

  addSteps(steps) {
    const list = document.createElement("ol");
    list.className = "steps";

    for (const step of steps) {
      const item = document.createElement("li");
      const description = document.createElement("p");
      description.textContent = step.description;
      item.append(description);
      if (step.matrix) {
        item.append(this.scrollBox(this.matrixTable(step.matrix)));
      }
      list.append(item);
    }
    this.addPanel("Steps", list);
  }

  matrixTable(matrix) {
    const table = document.createElement("table");
    table.className = "matrix";

    for (const row of matrix) {
      const tableRow = document.createElement("tr");
      row.forEach((value, index) => {
        const cell = document.createElement("td");
        cell.textContent = formatNumber(value);
        if (index === row.length - 1) {
          cell.className = "constant";
        }
        tableRow.append(cell);
      });
      table.append(tableRow);
    }
    return table;
  }

  scrollBox(element) {
    const box = document.createElement("div");
    box.className = "scroll-x";
    box.append(element);
    return box;
  }

  addPanel(title, content) {
    const panel = document.createElement("section");
    panel.className = "panel";
    const heading = document.createElement("h2");
    heading.textContent = title;
    panel.append(heading, content);
    this.results.append(panel);
  }

  // History

  async loadHistory() {
    this.history.replaceChildren();
    try {
      const items = await this.api.getHistory(this.slug);
      if (items.length === 0) {
        this.addHistoryMessage("Nothing saved yet.");
      }
      for (const item of items) {
        this.addHistoryRow(item);
      }
    } catch (error) {
      this.addHistoryMessage(error.message);
    }
  }

  addHistoryMessage(text) {
    const row = document.createElement("li");
    row.className = "history-empty";
    row.textContent = text;
    this.history.append(row);
  }

  addHistoryRow(item) {
    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "history-open";
    openButton.addEventListener("click", () => this.openCalculation(item.id));

    const summary = document.createElement("span");
    summary.className = "mono";
    summary.textContent = item.summary;

    const time = document.createElement("span");
    time.className = "history-time";
    time.textContent = item.created_at;
    openButton.append(summary, time);

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "history-delete";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("aria-label", "Delete " + item.summary);
    deleteButton.addEventListener("click", () => this.deleteCalculation(item.id));

    const row = document.createElement("li");
    row.append(openButton, deleteButton);
    this.history.append(row);
  }

  async openCalculation(id) {
    this.results.classList.add("is-loading");
    try {
      const calculation = await this.api.getCalculation(id);
      this.fillInputs(calculation.inputs);
      this.showResult(calculation.result);
    } catch (error) {
      this.showError(error.message);
    }
  }

  async deleteCalculation(id) {
    try {
      await this.api.deleteCalculation(id);
    } catch (error) {
      this.showError(error.message);
    }
    await this.loadHistory();
  }
}

new MethodPage();
