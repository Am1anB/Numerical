class HomePage {
  constructor() {
    this.select = document.getElementById("topic-select");
    this.select.addEventListener("change", () => this.openTopic());

    // Reset the dropdown when coming back with the browser's back button.
    window.addEventListener("pageshow", () => {
      this.select.value = "";
    });
  }

  openTopic() {
    if (this.select.value) {
      window.location.href = "/methods/" + this.select.value;
    }
  }
}

new HomePage();
