from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    send_file,
    flash,
)
import os
import logging
from werkzeug.utils import secure_filename
import shutil
import threading

from models.portfolio import PortfolioManager
from utils.data_loader import DataLoader

# --- App Configuration ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DEMO_DATA_FOLDER"] = "data"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DEMO_DATA_FOLDER"], exist_ok=True)
logging.basicConfig(level=logging.INFO)

PORTFOLIO_CACHE = {}
ANALYSIS_STATUS = {}

def get_user_upload_path():
    """Returns the path for the current user's uploaded files."""
    if "user_id" not in session:
        session["user_id"] = os.urandom(8).hex()
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["user_id"])
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def run_analysis_for_user(user_id, user_path):
    """The background task that runs the portfolio analysis."""
    try:
        data_loader = DataLoader(data_path=user_path)
        manager = PortfolioManager(data_loader=data_loader)
        PORTFOLIO_CACHE[user_id] = manager
        ANALYSIS_STATUS[user_id] = {'status': 'complete'}
        logging.info(f"Analysis complete for user {user_id}")
    except Exception as e:
        logging.error(f"Analysis failed for user {user_id}: {e}")
        ANALYSIS_STATUS[user_id] = {'status': 'error', 'message': str(e)}

def get_portfolio_manager():
    """Gets a completed PortfolioManager instance for the current user."""
    user_id = session.get("user_id")
    return PORTFOLIO_CACHE.get(user_id)

@app.context_processor
def inject_data_status():
    """Makes 'has_data' available to all templates for conditional rendering."""
    has_data = get_portfolio_manager() is not None
    return dict(has_data=has_data)

# --- Core Routes ---
@app.route("/", methods=["GET", "POST"])
def upload_page():
    user_path = get_user_upload_path()
    if request.method == "POST":
        if "files" not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)
        files = request.files.getlist("files")
        if not files or files[0].filename == "":
            flash("No files selected for uploading.", "warning")
            return redirect(request.url)
        
        if os.path.exists(user_path): shutil.rmtree(user_path)
        os.makedirs(user_path)
        
        user_id = session.get("user_id")
        if user_id in PORTFOLIO_CACHE: del PORTFOLIO_CACHE[user_id]
        if user_id in ANALYSIS_STATUS: del ANALYSIS_STATUS[user_id]
            
        for file in files:
            if file and file.filename.endswith(".csv"):
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_path, filename))
        
        return redirect(url_for("loading_page"))

    uploaded_files = [f for f in os.listdir(user_path) if f.endswith(".csv")]
    return render_template("uploads.html", uploaded_files=uploaded_files)

@app.route('/loading')
def loading_page():
    user_id = session.get("user_id")
    user_path = get_user_upload_path()
    
    if user_id not in ANALYSIS_STATUS:
        ANALYSIS_STATUS[user_id] = {'status': 'running'}
        thread = threading.Thread(target=run_analysis_for_user, args=(user_id, user_path))
        thread.daemon = True
        thread.start()
        
    return render_template('loading.html')

@app.route("/dashboard")
def dashboard():
    portfolio_manager = get_portfolio_manager()
    if portfolio_manager is None:
        flash("Your data has not been processed yet. Please upload files first.", "info")
        return redirect(url_for("upload_page"))
    summary = portfolio_manager.get_portfolio_summary()
    return render_template("dashboard.html", summary=summary)

@app.route('/holdings')
def holdings_page():
    if not inject_data_status()['has_data']: return redirect(url_for('upload_page'))
    return render_template('holdings.html')

@app.route('/splits')
def splits_page():
    if not inject_data_status()['has_data']: return redirect(url_for('upload_page'))
    return render_template('splits.html')

@app.route("/download-demo-data")
def download_demo_data():
    demo_file = "demo_trades.csv"
    demo_file_path = os.path.join(app.config["DEMO_DATA_FOLDER"], demo_file)
    if not os.path.exists(demo_file_path):
        flash("Demo file is not available.", "warning")
        return redirect(url_for('upload_page'))
    return send_file(demo_file_path, as_attachment=True)

@app.route("/clear-data", methods=["POST"])
def clear_data():
    user_path = get_user_upload_path()
    if os.path.exists(user_path):
        shutil.rmtree(user_path)
    
    user_id = session.get("user_id")
    if user_id in PORTFOLIO_CACHE: del PORTFOLIO_CACHE[user_id]
    if user_id in ANALYSIS_STATUS: del ANALYSIS_STATUS[user_id]
        
    flash("Your uploaded data has been cleared.", "success")
    return redirect(url_for("upload_page"))

@app.route('/api/analysis-status')
def api_analysis_status():
    user_id = session.get("user_id")
    return jsonify(ANALYSIS_STATUS.get(user_id, {'status': 'pending'}))

@app.route('/api/portfolio-value/<currency>')
def api_portfolio_value(currency):
    pm = get_portfolio_manager()
    if not pm: return jsonify({'error': 'No data found'}), 404
    return jsonify(pm.get_portfolio_value_history(currency))

@app.route('/api/holdings')
def api_holdings():
    pm = get_portfolio_manager()
    if not pm: return jsonify({'error': 'No data found'}), 404
    return jsonify(pm.get_holdings_with_xirr())
    
@app.route('/api/splits-analysis')
def api_splits_analysis():
    pm = get_portfolio_manager()
    if not pm: return jsonify({'error': 'No data found'}), 404
    return jsonify(pm.get_splits_analysis())

@app.route('/api/holdings-detailed')
def api_holdings_detailed():
    pm = get_portfolio_manager()
    if not pm: return jsonify({'holdings': {}, 'total_portfolio_value': 0}), 404
    
    holdings_data = pm.get_detailed_holdings()
    return jsonify(holdings_data)

if __name__ == "__main__":
    app.run(debug=True)
