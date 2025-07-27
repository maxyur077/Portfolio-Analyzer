// static/js/charts.js (Complete fixed version)
let myAreaChart;
let myPieChart;

// Chart.js Configuration
Chart.defaults.font.family =
  'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = "#858796";

// Initialize all charts
async function initializeCharts() {
  const isLoading = await checkDataLoading();
  if (!isLoading) {
    await loadPortfolioChart();
    await loadHoldingsPieChart();
    await loadHoldingsData();
  }
}

// Check if data is still loading
async function checkDataLoading() {
  try {
    const response = await fetch("/api/loading-status");
    const data = await response.json();
    return !data.loading_complete;
  } catch (error) {
    console.error("Error checking loading status:", error);
    return false;
  }
}

// Portfolio Area Chart
async function loadPortfolioChart(currency = "USD") {
  try {
    const response = await fetch(`/api/portfolio-value/${currency}`);
    if (response.status === 202) {
      console.log("Data still loading...");
      return;
    }

    const data = await response.json();
    console.log("Portfolio chart data:", data); // Debug log

    const ctx = document.getElementById("myAreaChart");
    if (!ctx) {
      console.error("Chart canvas not found");
      return;
    }

    // Destroy existing chart
    if (myAreaChart) {
      myAreaChart.destroy();
    }

    // Ensure we have data
    if (!data.dates || !data.values || data.dates.length === 0) {
      console.error("No chart data available");
      return;
    }

    myAreaChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.dates,
        datasets: [
          {
            label: `Portfolio Value (${currency})`,
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(78, 115, 223, 1)",
            pointRadius: 3,
            pointBackgroundColor: "rgba(78, 115, 223, 1)",
            pointBorderColor: "rgba(78, 115, 223, 1)",
            pointHoverRadius: 3,
            pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
            pointHoverBorderColor: "rgba(78, 115, 223, 1)",
            pointHitRadius: 10,
            pointBorderWidth: 2,
            data: data.values,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 25,
            top: 25,
            bottom: 0,
          },
        },
        scales: {
          x: {
            time: {
              unit: "date",
            },
            grid: {
              display: false,
              drawBorder: false,
            },
            ticks: {
              maxTicksLimit: 7,
            },
          },
          y: {
            ticks: {
              maxTicksLimit: 5,
              padding: 10,
              callback: function (value, index, values) {
                return currency === "USD"
                  ? "$" + number_format(value)
                  : "S$" + number_format(value);
              },
            },
            grid: {
              color: "rgb(234, 236, 244)",
              zeroLineColor: "rgb(234, 236, 244)",
              drawBorder: false,
              borderDash: [2],
              zeroLineBorderDash: [2],
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgb(255,255,255)",
            bodyColor: "#858796",
            titleMarginBottom: 10,
            titleColor: "#6e707e",
            titleFont: {
              size: 14,
            },
            borderColor: "#dddfeb",
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: "index",
            caretPadding: 10,
            callbacks: {
              label: function (context) {
                var label = context.dataset.label || "";
                if (label) {
                  label += ": ";
                }
                const prefix = currency === "USD" ? "$" : "S$";
                label += prefix + number_format(context.parsed.y);
                return label;
              },
            },
          },
        },
      },
    });

    console.log("Portfolio chart loaded successfully");
  } catch (error) {
    console.error("Error loading portfolio chart:", error);
  }
}

// Holdings Pie Chart
async function loadHoldingsPieChart() {
  try {
    const response = await fetch("/api/holdings");
    if (response.status === 202) {
      console.log("Holdings data still loading...");
      return;
    }

    const holdings = await response.json();
    console.log("Holdings data:", holdings); // Debug log

    const ctx = document.getElementById("myPieChart");
    if (!ctx) {
      console.error("Pie chart canvas not found");
      return;
    }

    if (!holdings || Object.keys(holdings).length === 0) {
      console.error("No holdings data available");
      return;
    }

    const topHoldings = Object.entries(holdings)
      .sort(([, a], [, b]) => b.market_value - a.market_value)
      .slice(0, 5);

    const labels = topHoldings.map(([symbol]) => symbol);
    const values = topHoldings.map(([, data]) => data.market_value);
    const colors = ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"];

    // Destroy existing chart
    if (myPieChart) {
      myPieChart.destroy();
    }

    myPieChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: colors,
            hoverBackgroundColor: colors.map((color) => color + "CC"),
            hoverBorderColor: "rgba(234, 236, 244, 1)",
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            backgroundColor: "rgb(255,255,255)",
            bodyColor: "#858796",
            borderColor: "#dddfeb",
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed;
                return label + ": $" + number_format(value);
              },
            },
          },
          legend: {
            display: false,
          },
        },
        cutout: "80%",
      },
    });

    console.log("Pie chart loaded successfully");
  } catch (error) {
    console.error("Error loading holdings pie chart:", error);
  }
}

// Load holdings data for table
async function loadHoldingsData() {
  try {
    const response = await fetch("/api/holdings");
    if (response.status === 202) {
      return; // Still loading
    }

    const holdings = await response.json();
    console.log("Table holdings data:", holdings); // Debug log

    const tbody = document.getElementById("holdingsTableBody");
    if (!tbody) return;

    if (holdings && Object.keys(holdings).length > 0) {
      tbody.innerHTML = Object.entries(holdings)
        .map(
          ([symbol, data]) => `
                <tr>
                    <td><strong>${symbol}</strong></td>
                    <td>${number_format(data.quantity, 2)}</td>
                    <td>$${number_format(data.avg_cost, 2)}</td>
                    <td>$${number_format(data.current_price, 2)}</td>
                    <td>$${number_format(data.market_value, 2)}</td>
                    <td class="${
                      data.unrealized_pnl >= 0 ? "text-success" : "text-danger"
                    }">
                        ${data.unrealized_pnl >= 0 ? "+" : ""}$${number_format(
            data.unrealized_pnl,
            2
          )}
                    </td>
                    <td>${
                      data.xirr ? (data.xirr * 100).toFixed(1) + "%" : "N/A"
                    }</td>
                </tr>
            `
        )
        .join("");
    } else {
      tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        No holdings data available
                    </td>
                </tr>
            `;
    }

    console.log("Holdings table loaded successfully");
  } catch (error) {
    console.error("Error loading holdings data:", error);
    const tbody = document.getElementById("holdingsTableBody");
    if (tbody) {
      tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger">
                        Error loading holdings data
                    </td>
                </tr>
            `;
    }
  }
}

// Number formatting function
function number_format(number, decimals, dec_point, thousands_sep) {
  number = (number + "").replace(",", "").replace(" ", "");
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = typeof thousands_sep === "undefined" ? "," : thousands_sep,
    dec = typeof dec_point === "undefined" ? "." : dec_point,
    s = "",
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return "" + Math.round(n * k) / k;
    };
  s = (prec ? toFixedFix(n, prec) : "" + Math.round(n)).split(".");
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || "").length < prec) {
    s[1] = s[1] || "";
    s[1] += new Array(prec - s[1].length + 1).join("0");
  }
  return s.join(dec);
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM loaded, initializing charts...");
  initializeCharts();
});

// Add error handling for missing Chart.js
if (typeof Chart === "undefined") {
  console.error("Chart.js not loaded!");
}
