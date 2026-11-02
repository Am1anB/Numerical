class Api {
  async send(url, options) {
    let response;
    try {
      response = await fetch(url, options);
    } catch {
      throw new Error("Could not connect to the server.");
    }

    if (response.status === 204) {
      return null;
    }

    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error);
    }
    return body;
  }

  calculate(slug, inputs) {
    return this.send(`/api/methods/${slug}/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inputs),
    });
  }

  getHistory(slug) {
    return this.send(`/api/calculations?method=${slug}&limit=10`);
  }

  getCalculation(id) {
    return this.send(`/api/calculations/${id}`);
  }

  deleteCalculation(id) {
    return this.send(`/api/calculations/${id}`, { method: "DELETE" });
  }
}
