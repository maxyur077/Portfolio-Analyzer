
import numpy as np
from scipy.optimize import newton
from datetime import datetime
import logging
import math

def calculate_xirr(cashflows, dates, guess=0.1):
    """
    Calculate XIRR (Extended Internal Rate of Return)
    """
    try:
        if len(cashflows) != len(dates):
            raise ValueError("Cashflows and dates must have same length")
        
        if len(cashflows) < 2:
            return None
        
        
        cashflows = np.array(cashflows, dtype=float)
        
        
        if np.all(cashflows == 0) or np.any(np.isnan(cashflows)) or np.any(np.isinf(cashflows)):
            logging.warning("Invalid cashflows detected")
            return None
        
        
        first_date = min(dates)
        days = np.array([(d - first_date).days for d in dates], dtype=float)
        
        def xnpv(rate, cashflows, days):
            """Calculate Net Present Value for given rate"""
            if rate <= -1:  
                return float('inf')
            
            try:
                powers = days / 365.0
                
                if np.any(powers < 0) or rate <= -1:
                    return float('inf')
                
                return np.sum(cashflows / ((1 + rate) ** powers))
            except (OverflowError, RuntimeWarning):
                return float('inf')
        
        def xnpv_derivative(rate, cashflows, days):
            """Calculate derivative of NPV for Newton's method"""
            if rate <= -1:
                return float('inf')
                
            try:
                powers = days / 365.0
                return np.sum(-cashflows * powers / ((1 + rate) ** (powers + 1)))
            except (OverflowError, RuntimeWarning):
                return float('inf')
        
        
        initial_guesses = [0.1, 0.05, 0.2, -0.1, 0.01]
        
        for initial_guess in initial_guesses:
            try:
                
                result = newton(
                    lambda r: xnpv(r, cashflows, days), 
                    initial_guess, 
                    fprime=lambda r: xnpv_derivative(r, cashflows, days),
                    maxiter=100,
                    tol=1e-6
                )
                
                
                if not np.isnan(result) and not np.isinf(result) and result > -0.99:
                    return float(result)
                    
            except Exception as e:
                logging.debug(f"XIRR calculation failed with guess {initial_guess}: {e}")
                continue
        
        
        try:
            total_invested = -np.sum(cashflows[cashflows < 0])
            final_value = cashflows[-1]
            
            if total_invested > 0 and final_value > 0:
                years = days[-1] / 365.0
                if years > 0:
                    simple_return = (final_value / total_invested) ** (1/years) - 1
                    return float(simple_return) if not np.isnan(simple_return) else None
        except:
            pass
        
        logging.warning("XIRR calculation failed with all methods")
        return None
        
    except Exception as e:
        logging.error(f"XIRR calculation failed: {e}")
        return None
