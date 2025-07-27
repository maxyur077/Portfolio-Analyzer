
from flask import Flask, render_template, jsonify
import pandas as pd
from models.portfolio import PortfolioManager
from utils.data_loader import DataLoader
import logging
import time
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


portfolio_manager = None
data_loading_complete = False
loading_error = None

def initialize_portfolio_data():
    """Initialize portfolio data in background"""
    global portfolio_manager, data_loading_complete, loading_error
    
    try:
        logging.info("Starting portfolio data initialization...")
        time.sleep(random.uniform(1, 2))  
        
        data_loader = DataLoader()
        portfolio_manager = PortfolioManager(data_loader)
        
        data_loading_complete = True
        logging.info("Portfolio data initialization completed successfully")
        
    except Exception as e:
        loading_error = str(e)
        logging.error(f"Error initializing portfolio data: {e}")


import threading
thread = threading.Thread(target=initialize_portfolio_data)
thread.daemon = True
thread.start()

@app.route('/')
def dashboard():
    """Main dashboard with portfolio overview"""
    if not data_loading_complete:
        return render_template('dashboard.html', 
                             loading=True, 
                             error=loading_error,
                             summary={'total_holdings': 0, 'total_value_usd': 0, 'total_value_sgd': 0, 'total_unrealized_pnl': 0, 'top_holdings': []})
    
    try:
        portfolio_summary = portfolio_manager.get_portfolio_summary()
        daily_values = portfolio_manager.get_daily_portfolio_values()
        
        return render_template('dashboard.html', 
                             loading=False,
                             error=None,
                             summary=portfolio_summary,
                             daily_values=daily_values)
    except Exception as e:
        logging.error(f"Error in dashboard: {e}")
        return render_template('dashboard.html', 
                             loading=False, 
                             error=str(e),
                             summary={'total_holdings': 0, 'total_value_usd': 0, 'total_value_sgd': 0, 'total_unrealized_pnl': 0, 'top_holdings': []})

@app.route('/holdings')
def holdings_page():
    """Renders the detailed holdings page"""
    return render_template('holdings.html', loading=not data_loading_complete, error=loading_error)

@app.route('/splits')
def splits_page():
    """Renders the split analysis page"""
    return render_template('splits.html', loading=not data_loading_complete, error=loading_error)


@app.route('/api/loading-status')
def api_loading_status():
    """Check if data loading is complete"""
    return jsonify({
        'loading_complete': data_loading_complete,
        'error': loading_error
    })

@app.route('/api/holdings')
def api_holdings():
    """API endpoint for holdings data"""
    if not data_loading_complete:
        return jsonify({'error': 'Data still loading', 'loading': True}), 202
    
    try:
        holdings = portfolio_manager.get_holdings_with_xirr()
        return jsonify(holdings)
    except Exception as e:
        logging.error(f"Error getting holdings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio-value/<currency>')
def api_portfolio_value(currency):
    """API endpoint for portfolio value in specific currency"""
    if not data_loading_complete:
        return jsonify({'error': 'Data still loading', 'loading': True}), 202
    
    try:
        values = portfolio_manager.get_portfolio_value_history(currency)
        return jsonify(values)
    except Exception as e:
        logging.error(f"Error getting portfolio value: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/splits-analysis')
def api_splits_analysis():
    """API endpoint for split analysis data"""
    if not data_loading_complete:
        return jsonify({'error': 'Data still loading', 'loading': True}), 202
    
    try:
        splits_data = portfolio_manager.get_splits_analysis()
        return jsonify(splits_data)
    except Exception as e:
        logging.error(f"Error getting splits analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/holdings-detailed')
def api_holdings_detailed():
    """API endpoint for detailed holdings data"""
    if not data_loading_complete:
        return jsonify({'error': 'Data still loading', 'loading': True}), 202
    
    try:
        holdings = portfolio_manager.get_holdings_with_xirr()
        total_value = sum(h['market_value'] for h in holdings.values())
        
        return jsonify({
            'holdings': holdings,
            'total_portfolio_value': total_value
        })
    except Exception as e:
        logging.error(f"Error getting detailed holdings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/holding-detail/<symbol>')
def api_holding_detail(symbol):
    if not data_loading_complete:
        return jsonify({'loading': True}), 202
    data = portfolio_manager.get_holding_details(symbol)
    return jsonify(data)          
@app.route('/api/refresh-prices', methods=['POST'])
def api_refresh_prices():
    """API endpoint to refresh all portfolio prices"""
    if not data_loading_complete:
        return jsonify({'error': 'Data still loading'}), 202
    
    try:
        
        import threading
        def refresh_in_background():
            portfolio_manager.refresh_prices()
        
        thread = threading.Thread(target=refresh_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Price refresh started'})
    except Exception as e:
        logging.error(f"Error refreshing prices: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
