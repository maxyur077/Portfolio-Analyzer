# Portfolio Analyzer 📊

A modern, session-based web application built with Flask and JavaScript that allows users to upload their trade history and receive a comprehensive, interactive analysis of their investment portfolio.

_(Note: Replace this with a real screenshot of your application's dashboard)_

---

## ✨ Features

- **Secure, Session-Based Data Handling**: Each user's data is stored in a unique session, ensuring privacy and isolation.
- **Dynamic File Uploads**: Users can upload one or multiple CSV trade history files.
- **Background Processing with Loading Screen**: After uploading, a non-blocking loading page provides a smooth user experience while data is analyzed in the background.
- **Interactive Dashboard**: A clean, single-page dashboard visualizes key portfolio metrics:
  - Summary cards (Total Holdings, Value in USD/SGD, Unrealized P&L).
  - A historical portfolio value chart (Line Chart).
  - A holdings breakdown by market value (Doughnut Chart).
- **Real-time Price Refresh**: A "Refresh Prices" button fetches the latest market data for all holdings without requiring a page reload.
- **Detailed Data Views**:
  - **All Holdings Page**: A detailed, sortable table of all holdings with XIRR calculations.
  - **Split Analysis Page**: A dedicated view to show all detected stock splits, their impact on prices, and the number of trades adjusted.
- **Demo Data**: Users can download a sample CSV file to understand the required format.
- **Easy Data Management**: A "Clear Data" button allows users to easily delete their uploaded files and start over.

---

## 🛠️ Tech Stack

- **Backend**:
  - **Python 3**
  - **Flask**: For the web server and API endpoints.
  - **Pandas**: For data manipulation and analysis.
  - **yfinance**: For fetching stock prices and split data.
- **Frontend**:
  - **HTML5 / CSS3**
  - **JavaScript (ES6+)**: For dynamic content loading and interactivity.
  - **Bootstrap 5**: For responsive design and UI components.
  - **Chart.js**: for creating interactive charts.
  - **Font Awesome**: For icons.

---

## 🚀 Getting Started

Follow these instructions to get the application running on your local machine.

### Prerequisites

- Python 3.8 or higher

### Installation & Setup

1.  **Clone the repository:**

    ```
    git clone https://github.com/your-username/portfolio-analyzer.git
    cd portfolio-analyzer
    ```

2.  **Create and activate a virtual environment:**

    - **macOS / Linux:**
      ```
      python3 -m venv venv
      source venv/bin/activate
      ```
    - **Windows:**
      ```
      python -m venv venv
      .\venv\Scripts\activate
      ```

3.  **Install the required packages:**

    > **Note:** A `requirements.txt` file is included. If you add new packages, you can regenerate it with `pip freeze > requirements.txt`.

    ```
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

---

## 🎈 How to Use

1.  Navigate to the home page (`http://127.0.0.1:5000`).
2.  If you're unsure of the file format, click **"Download Demo File"**.
3.  Click **"Choose Files"** and select one or more of your trade history CSV files.
4.  Click **"Upload & Analyze"**.
5.  You will see a loading screen while your data is processed. Once complete, you will be redirected to the dashboard.
6.  Explore your portfolio using the **Dashboard**, **All Holdings**, and **Split Analysis** links in the navbar.
7.  To start over, return to the home page by clicking the logo and use the **"Clear All Data"** button.
