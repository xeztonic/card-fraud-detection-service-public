// Reads backend route URLs from the body data attributes.
function getRoutes() {
  return document.body.dataset;
}

// Fills the form with a legitimate transaction example.
function fillLegitimateExample() {
  fillSimulationForm({
    TransactionAmt: 25,
    TransactionDT: 45000,
    card1: 10095,
    card2: 111,
    card4: "visa",
    addr1: 315,
    P_emaildomain: "gmail.com",
    dist1: 1,
    ProductCD: "W"
  });
}

// Fills the form with a suspicious transaction example.
function fillSuspiciousExample() {
  fillSimulationForm({
    TransactionAmt: 950,
    TransactionDT: 900000,
    card1: 9633,
    card2: 555,
    card4: "mastercard",
    addr1: 999,
    P_emaildomain: "yahoo.com",
    dist1: 120,
    ProductCD: "C"
  });
}

// Fills the form with a high-risk transaction example.
function fillHighRiskExample() {
  fillSimulationForm({
    TransactionAmt: 5000,
    TransactionDT: 1500000,
    card1: 15066,
    card2: 490,
    card4: "discover",
    addr1: 999,
    P_emaildomain: "mail.com",
    dist1: 500,
    ProductCD: "C"
  });
}

// Applies preset values to the simulation form fields.
function fillSimulationForm(values) {
  Object.entries(values).forEach(function ([fieldId, value]) {
    const input = document.getElementById(fieldId);

    if (input) {
      input.value = value;
    }
  });
}

// Clears the simulation result and reloads the empty form.
function resetSimulationForm() {
  const routes = getRoutes();

  window.location.href = routes.simulateUrl;
}

// Displays the selected CSV filename inside the import popup.
function showSelectedFileName() {
  const input = document.getElementById("csvFileInput");
  const fileName = document.getElementById("selectedFileName");

  if (!input || !fileName) {
    return;
  }

  if (input.files.length > 0) {
    fileName.textContent = input.files[0].name;
  } else {
    fileName.textContent = "No CSV file selected.";
  }
}

// Connects preset buttons to the form autofill examples.
function setupPresetButtons() {
  const legitimateButton = document.getElementById("legitimateExampleBtn");
  const suspiciousButton = document.getElementById("suspiciousExampleBtn");
  const highRiskButton = document.getElementById("highRiskExampleBtn");

  if (legitimateButton) {
    legitimateButton.addEventListener("click", fillLegitimateExample);
  }

  if (suspiciousButton) {
    suspiciousButton.addEventListener("click", fillSuspiciousExample);
  }

  if (highRiskButton) {
    highRiskButton.addEventListener("click", fillHighRiskExample);
  }
}

// Connects the refresh button to the form reset action.
function setupResetButton() {
  const resetButton = document.getElementById("resetSimulationFormBtn");

  if (resetButton) {
    resetButton.addEventListener("click", resetSimulationForm);
  }
}

// Connects the CSV input to the selected filename display.
function setupImportFileName() {
  const csvInput = document.getElementById("csvFileInput");

  if (csvInput) {
    csvInput.addEventListener("change", showSelectedFileName);
  }
}

// Shows loading state when the CSV import form is submitted.
function setupImportLoadingState() {
  const importForm = document.getElementById("importCsvForm");
  const submitButton = document.getElementById("importCsvSubmitBtn");
  const loadingMessage = document.getElementById("importLoadingMessage");

  if (!importForm || !submitButton || !loadingMessage) {
    return;
  }

  importForm.addEventListener("submit", function () {
    submitButton.disabled = true;
    submitButton.textContent = "Importing...";
    loadingMessage.classList.add("active");
  });
}

// Initializes all simulation page interactions.
function initializeSimulationPage() {
  setupPresetButtons();
  setupResetButton();
  setupImportFileName();
  setupImportLoadingState();
}

// Runs the simulation page initialization once the DOM is ready.
document.addEventListener("DOMContentLoaded", initializeSimulationPage);