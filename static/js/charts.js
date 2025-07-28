let myAreaChart;
let myPieChart;

Chart.defaults.font.family =
  'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = "#858796";

async function initializeCharts() {
  const isLoading = await checkDataLoading();
  if (!isLoading) {
    await Promise.all([
      loadPortfolioSummary(),
      loadPortfolioChart(),
      loadHoldingsPieChart(),
      loadHoldingsData(),
      loadDashboardNews(),
    ]);
  }
}

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

async function loadPortfolioSummary() {
  try {
    const response = await fetch("/api/portfolio-summary");
    if (response.status === 202) {
      console.log("Summary data still loading...");
      return;
    }

    const summary = await response.json();

    document.getElementById("total-holdings").textContent =
      summary.total_holdings;
    document.getElementById("value-usd").textContent =
      "$" + number_format(summary.total_value_usd, 2);
    document.getElementById("value-sgd").textContent =
      "S$" + number_format(summary.total_value_sgd, 2);

    const pnlElement = document.getElementById("unrealized-pnl");
    const pnlValue = summary.total_unrealized_pnl;
    const pnlClass = pnlValue >= 0 ? "text-success" : "text-danger";
    const pnlSign = pnlValue >= 0 ? "+" : "";

    pnlElement.className = `h5 mb-0 font-weight-bold ${pnlClass}`;
    pnlElement.textContent = `${pnlSign}$${number_format(pnlValue, 2)}`;

    console.log("Portfolio summary loaded successfully");
  } catch (error) {
    console.error("Error loading portfolio summary:", error);
  }
}

async function loadDashboardNews() {
  const loadingEl = document.getElementById("news-loading");
  const errorEl = document.getElementById("news-error");
  const emptyEl = document.getElementById("news-empty");
  const contentEl = document.getElementById("news-content");
  const refreshBtn = document.getElementById("news-refresh-btn");

  showNewsState("loading");

  if (refreshBtn) {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Loading...';
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000);

    const response = await fetch("/api/portfolio-news", {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const newsData = await response.json();

    if (!newsData || Object.keys(newsData).length === 0) {
      showNewsState("empty");
      return;
    }

    const allArticles = [];
    for (const [symbol, articles] of Object.entries(newsData)) {
      articles.forEach((article) => {
        allArticles.push({ ...article, symbol });
      });
      if (allArticles.length >= 4) break;
    }

    const topArticles = allArticles.slice(0, 4);

    if (topArticles.length === 0) {
      showNewsState("empty");
      return;
    }

    populateNewsArticles(topArticles);
    showNewsState("content");

    console.log("Dashboard news loaded successfully");
  } catch (error) {
    console.error("Error loading dashboard news:", error);

    const errorMessage =
      error.name === "AbortError"
        ? "News loading timed out."
        : "Unable to load news at this time.";

    document.getElementById("news-error-message").textContent = errorMessage;
    showNewsState("error");
  } finally {
    if (refreshBtn) {
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
    }
  }
}

function showNewsState(state) {
  const states = ["loading", "error", "empty", "content"];

  states.forEach((s) => {
    const element = document.getElementById(`news-${s}`);
    if (element) {
      element.style.display = s === state ? "block" : "none";
    }
  });
}

function populateNewsArticles(articles) {
  const contentEl = document.getElementById("news-content");
  const template = document.getElementById("news-article-template");

  if (!template) {
    console.error("News article template not found");
    return;
  }

  contentEl.innerHTML = "";

  articles.forEach((article) => {
    const clone = template.content.cloneNode(true);

    const publishedDate = new Date(article.publishedAt).toLocaleDateString();
    const truncatedTitle =
      article.title.length > 60
        ? article.title.substring(0, 60) + "..."
        : article.title;
    const truncatedDescription =
      article.description.length > 100
        ? article.description.substring(0, 100) + "..."
        : article.description;

    clone.querySelector(".news-symbol").textContent = article.symbol;
    clone.querySelector(".news-date").textContent = publishedDate;
    clone.querySelector(".news-title").textContent = truncatedTitle;
    clone.querySelector(".news-title-link").href = article.url;
    clone.querySelector(".news-description").textContent = truncatedDescription;
    clone.querySelector(".news-source").textContent = article.source;
    clone.querySelector(".news-read-link").href = article.url;

    contentEl.appendChild(clone);
  });
}

async function loadPortfolioChart(currency = "USD") {
  try {
    const response = await fetch(`/api/portfolio-value/${currency}`);
    if (response.status === 202) {
      console.log("Data still loading...");
      return;
    }

    const data = await response.json();
    console.log("Portfolio chart data:", data);

    const ctx = document.getElementById("myAreaChart");
    if (!ctx) {
      console.error("Chart canvas not found");
      return;
    }

    if (myAreaChart) {
      myAreaChart.destroy();
    }

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

async function loadHoldingsPieChart() {
  try {
    const response = await fetch("/api/holdings");
    if (response.status === 202) {
      console.log("Holdings data still loading...");
      return;
    }

    const holdings = await response.json();
    console.log("Holdings data:", holdings);

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

async function loadHoldingsData() {
  try {
    const response = await fetch("/api/holdings");
    if (response.status === 202) {
      return;
    }

    const holdings = await response.json();
    console.log("Table holdings data:", holdings);

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

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM loaded, initializing charts...");
  initializeCharts();
});

if (typeof Chart === "undefined") {
  console.error("Chart.js not loaded!");
}
