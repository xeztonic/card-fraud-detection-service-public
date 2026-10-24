// Stores the Chart.js instance after the live chart is created.
let liveChart = null;

// Stores the interval used for live monitoring.
let liveInterval = null;

// Prevents overlapping live requests.
let isUpdating = false;

// Stores the latest transactions displayed in the live chart.
let liveChartTransactions = [];

// Reads backend route URLs from the body data attributes.
function getRoutes() {
  return document.body.dataset;
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

// Returns the point color used in the live chart based on the risk category.
function getPointColor(category) {
  if (category === "High Risk") {
    return "#ef4444";
  }

  if (category === "Suspicious") {
    return "#f59e0b";
  }

  return "#22c55e";
}

// Returns the CSS badge class based on the risk category.
function getBadgeClass(category) {
  if (category === "High Risk") {
    return "badge-high-risk";
  }

  if (category === "Suspicious") {
    return "badge-suspicious";
  }

  return "badge-legitimate";
}

// Converts the risk factors text into a dropdown list.
function renderRiskFactors(riskFactors) {
  if (!riskFactors) {
    return "-";
  }

  const factors = riskFactors.split(", ");
  const items = factors.map((factor) => `<li>${factor}</li>`).join("");

  return `
    <details class="details-dropdown">
      <summary>View details</summary>
      <ul>${items}</ul>
    </details>
  `;
}

// Scrolls to a transaction row, or searches for it if it is not currently visible.
function scrollToTransactionRow(transactionId) {
  const routes = getRoutes();
  const row = document.getElementById(`transaction-row-${transactionId}`);

  if (row) {
    row.scrollIntoView({
      behavior: "smooth",
      block: "center"
    });

    row.classList.add("highlight-row");

    setTimeout(function () {
      row.classList.remove("highlight-row");
    }, 2000);
  } else {
    window.location.href =
      routes.dashboardUrl +
      "?search=" +
      encodeURIComponent(transactionId) +
      "#transactions";
  }
}

// Loads the latest transactions into the recent transactions table.
async function loadRecentTransactionsTable() {
  const routes = getRoutes();
  const urlParams = new URLSearchParams(window.location.search);

  const activeSearch = urlParams.get("search");
  const activeCategory = urlParams.get("category");
  const activePage = urlParams.get("page") || "1";

  if (
    activePage !== "1" ||
    activeSearch ||
    (activeCategory && activeCategory !== "All Risk Categories")
  ) {
    return;
  }

  const response = await fetch(routes.liveTableUrl);
  const transactions = await response.json();

  const tbody = document.getElementById("recentTransactionsBody");

  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";

  transactions.forEach(function (t) {
    const row = document.createElement("tr");
    row.id = `transaction-row-${t.id}`;

    row.innerHTML = `
      <td>${t.id}</td>
      <td>${t.transaction_amt ?? ""}</td>
      <td>${t.card1 ?? ""}</td>
      <td>${t.email ?? ""}</td>
      <td>${t.customer_email ?? ""}</td>
      <td>${t.risk_score ?? ""}</td>
      <td>
        <span class="risk-badge ${getBadgeClass(t.risk_category)}">
          ${t.risk_category}
        </span>
      </td>
      <td>${t.email_alert_sent ? "Sent" : "-"}</td>
      <td>${t.customer_alert_sent ? "Sent" : "-"}</td>
      <td>${renderRiskFactors(t.risk_factors)}</td>
    `;

    tbody.appendChild(row);
  });
}

// Loads data from the backend and renders or updates the live risk chart.
async function loadLiveChartData() {
  const routes = getRoutes();
  const response = await fetch(routes.liveChartUrl);
  const points = await response.json();

  liveChartTransactions = points;

  const labels = points.map(function (t) {
    return `#${t.id}`;
  });

  const scores = points.map(function (t) {
    return Number(t.risk_score);
  });

  const colors = points.map(function (t) {
    return getPointColor(t.risk_category);
  });

  const canvas = document.getElementById("liveRiskChart");

  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext("2d");

  canvas.width = Math.max(1600, points.length * 45);
  canvas.height = 500;

  if (!liveChart) {
    liveChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Risk Score",
            data: scores,
            borderColor: "#2563eb",
            borderWidth: 3,
            tension: 0.25,
            fill: false,
            pointRadius: 7,
            pointHoverRadius: 11,
            pointHitRadius: 14,
            pointBackgroundColor: colors,
            pointBorderColor: colors,
            pointBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        animation: false,
        interaction: {
          mode: "nearest",
          intersect: false
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: true,
            callbacks: {
              title: function (context) {
                const index = context[0].dataIndex;
                const point = liveChartTransactions[index];

                return `Transaction ID: ${point.id}`;
              },
              label: function (context) {
                const index = context.dataIndex;
                const point = liveChartTransactions[index];

                return [
                  `Risk Score: ${point.risk_score}`,
                  `Category: ${point.risk_category}`,
                  `Amount: ${point.transaction_amt || "-"}`,
                  `Card: ${point.card1 || "-"}`,
                  `Email: ${point.email || "-"}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            ticks: {
              font: {
                size: 12,
                weight: "600"
              },
              maxRotation: 0,
              minRotation: 0,
              autoSkip: false
            },
            title: {
              display: false
            }
          },
          y: {
            min: 0,
            max: 100,
            ticks: {
              stepSize: 10,
              font: {
                size: 12
              }
            },
            title: {
              display: false
            }
          }
        },
        onClick: function (event, elements) {
          if (elements.length > 0) {
            const pointIndex = elements[0].index;
            const transaction = liveChartTransactions[pointIndex];

            scrollToTransactionRow(transaction.id);
          }
        },
        onHover: function (event, elements) {
          const infoBox = document.getElementById("chartInfoBox");

          if (!infoBox) {
            return;
          }

          if (elements.length > 0) {
            const pointIndex = elements[0].index;
            const transaction = liveChartTransactions[pointIndex];

            infoBox.innerHTML = `
              <strong>Transaction ID:</strong> ${transaction.id}
              &nbsp; | &nbsp;
              <strong>Risk Score:</strong> ${transaction.risk_score}
              &nbsp; | &nbsp;
              <strong>Category:</strong> ${transaction.risk_category}
            `;

            event.native.target.style.cursor = "pointer";
          } else {
            infoBox.innerHTML =
              "Hover over a transaction point to view details.";

            event.native.target.style.cursor = "default";
          }
        }
      }
    });
  } else {
    liveChart.data.labels = labels;
    liveChart.data.datasets[0].data = scores;
    liveChart.data.datasets[0].pointBackgroundColor = colors;
    liveChart.data.datasets[0].pointBorderColor = colors;
    liveChart.update("none");
  }
}

// Updates the dashboard summary cards and risk category distribution bars.
async function loadDashboardStats() {
  const routes = getRoutes();
  const response = await fetch(routes.liveStatsUrl);
  const stats = await response.json();

  document.getElementById("totalTransactionsValue").textContent =
    stats.total_transactions;

  document.getElementById("averageRiskScoreValue").textContent =
    stats.average_risk_score;

  document.getElementById("alertsSentValue").textContent =
    stats.alerts_sent;

  document.getElementById("highRiskRateValue").textContent =
    stats.high_risk_rate;

  document.getElementById("legitimateCount").textContent =
    stats.legitimate_count;

  document.getElementById("suspiciousCount").textContent =
    stats.suspicious_count;

  document.getElementById("highRiskCount").textContent =
    stats.high_risk_count;

  document.getElementById("legitimateBar").style.width =
    stats.legitimate_percent + "%";

  document.getElementById("suspiciousBar").style.width =
    stats.suspicious_percent + "%";

  document.getElementById("highRiskBar").style.width =
    stats.high_risk_percent + "%";
}

// Processes one live transaction and refreshes dashboard data.
async function liveStep() {
  const routes = getRoutes();

  if (isUpdating) {
    return;
  }

  isUpdating = true;

  try {
    await fetch(routes.liveStepUrl, {
      method: "POST"
    });

    await loadLiveChartData();
    await loadRecentTransactionsTable();
    await loadDashboardStats();
  } catch (error) {
    console.error("Live update error:", error);
  } finally {
    isUpdating = false;
  }
}

// Starts the live transaction monitoring interval.
function startLiveMonitoring() {
  const status = document.getElementById("liveStatusText");

  if (liveInterval) {
    return;
  }

  localStorage.setItem("liveMonitoringEnabled", "true");

  if (status) {
    status.textContent = "Live monitoring is active.";
  }

  liveStep();

  liveInterval = setInterval(function () {
    liveStep();
  }, 1000);
}

// Stops the live transaction monitoring interval.
function stopLiveMonitoring() {
  const status = document.getElementById("liveStatusText");

  localStorage.setItem("liveMonitoringEnabled", "false");

  if (liveInterval) {
    clearInterval(liveInterval);
    liveInterval = null;
  }

  if (status) {
    status.textContent = "Live monitoring is stopped.";
  }
}

// Enables direct page navigation from the pagination input.
function setupPageJump() {
  const routes = getRoutes();
  const pageInput = document.getElementById("pageInput");

  if (!pageInput) {
    return;
  }

  pageInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();

      const page = this.value;
      const params = new URLSearchParams(window.location.search);

      params.set("page", page);

      window.location.href =
        routes.dashboardUrl + "?" + params.toString() + "#transactions";
    }
  });
}

// Connects the CSV file input to the selected filename display.
function setupImportFileName() {
  const csvInput = document.getElementById("csvFileInput");

  if (!csvInput) {
    return;
  }

  csvInput.addEventListener("change", showSelectedFileName);
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

// Hides import success or error messages after a short delay.
function setupImportMessage() {
  const message = document.getElementById("importMessage");

  if (!message) {
    return;
  }

  setTimeout(function () {
    message.style.display = "none";

    const params = new URLSearchParams(window.location.search);
    params.delete("imported");
    params.delete("import_error");

    const cleanUrl =
      window.location.pathname +
      (params.toString() ? "?" + params.toString() : "");

    window.history.replaceState({}, document.title, cleanUrl);
  }, 4000);
}

// Connects Start and Stop buttons to live monitoring.
function setupLiveButtons() {
  const startButton = document.getElementById("startLiveBtn");
  const stopButton = document.getElementById("stopLiveBtn");

  if (startButton) {
    startButton.addEventListener("click", startLiveMonitoring);
  }

  if (stopButton) {
    stopButton.addEventListener("click", stopLiveMonitoring);
  }
}

// Initializes all dashboard interactions after the page loads.
async function initializeDashboard() {
    setupImportMessage();
    setupImportFileName();
    setupImportLoadingState();
    setupPageJump();
    setupLiveButtons();

  await loadLiveChartData();
  await loadRecentTransactionsTable();
  await loadDashboardStats();

  const liveEnabled = localStorage.getItem("liveMonitoringEnabled");

  if (liveEnabled === "true") {
    startLiveMonitoring();
  } else {
    const status = document.getElementById("liveStatusText");

    if (status) {
      status.textContent = "Live monitoring is stopped.";
    }
  }
}

// Runs the dashboard initialization once the DOM is ready.
document.addEventListener("DOMContentLoaded", initializeDashboard);