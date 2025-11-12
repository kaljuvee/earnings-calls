"""
Yahoo Finance Client
Handles fetching analyst estimates, recommendations, and financial data
"""

import yfinance as yf
from typing import Optional, Dict, List
import pandas as pd


class YFinanceClient:
    """Client for Yahoo Finance data"""
    
    def __init__(self):
        """Initialize Yahoo Finance client"""
        pass
    
    def get_analyst_estimates(self, ticker: str) -> Optional[Dict]:
        """
        Get analyst estimates for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with analyst estimates data
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get earnings estimates
            earnings_estimate = stock.earnings_estimate
            revenue_estimate = stock.revenue_estimate
            
            # Get analyst recommendations
            recommendations = stock.recommendations
            
            # Get earnings history (actual vs estimate)
            earnings_history = stock.earnings_history
            
            return {
                "earnings_estimate": earnings_estimate.to_dict() if earnings_estimate is not None else None,
                "revenue_estimate": revenue_estimate.to_dict() if revenue_estimate is not None else None,
                "recommendations": recommendations.to_dict() if recommendations is not None else None,
                "earnings_history": earnings_history.to_dict() if earnings_history is not None else None
            }
            
        except Exception as e:
            print(f"Error fetching analyst estimates: {e}")
            return None
    
    def get_earnings_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Get earnings data including actual vs estimates
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with earnings data
        """
        try:
            stock = yf.Ticker(ticker)
            earnings = stock.earnings_dates
            return earnings
            
        except Exception as e:
            print(f"Error fetching earnings data: {e}")
            return None
    
    def get_analyst_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Get analyst recommendations summary
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with recommendations
        """
        try:
            stock = yf.Ticker(ticker)
            recommendations = stock.recommendations
            return recommendations
            
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            return None
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get company information
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with company info
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
            
        except Exception as e:
            print(f"Error fetching company info: {e}")
            return None
    
    def get_financial_statements(self, ticker: str) -> Dict:
        """
        Get financial statements (income statement, balance sheet, cash flow)
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with financial statements
        """
        try:
            stock = yf.Ticker(ticker)
            
            return {
                "income_statement": stock.income_stmt,
                "balance_sheet": stock.balance_sheet,
                "cash_flow": stock.cashflow,
                "quarterly_income_statement": stock.quarterly_income_stmt,
                "quarterly_balance_sheet": stock.quarterly_balance_sheet,
                "quarterly_cash_flow": stock.quarterly_cashflow
            }
            
        except Exception as e:
            print(f"Error fetching financial statements: {e}")
            return {}
    
    def compare_estimates_vs_actual(self, ticker: str, quarter: str = None) -> Optional[Dict]:
        """
        Compare analyst estimates vs actual results
        
        Args:
            ticker: Stock ticker symbol
            quarter: Specific quarter to analyze (optional)
            
        Returns:
            Dictionary with comparison data
        """
        try:
            stock = yf.Ticker(ticker)
            earnings_history = stock.earnings_history
            
            if earnings_history is None or earnings_history.empty:
                return None
            
            # Calculate surprises
            comparison = {
                "eps_estimate": [],
                "eps_actual": [],
                "eps_surprise": [],
                "eps_surprise_percent": [],
                "dates": []
            }
            
            for idx, row in earnings_history.iterrows():
                eps_estimate = row.get('epsEstimate', None)
                eps_actual = row.get('epsActual', None)
                
                if eps_estimate is not None and eps_actual is not None:
                    surprise = eps_actual - eps_estimate
                    surprise_pct = (surprise / abs(eps_estimate)) * 100 if eps_estimate != 0 else 0
                    
                    comparison["eps_estimate"].append(eps_estimate)
                    comparison["eps_actual"].append(eps_actual)
                    comparison["eps_surprise"].append(surprise)
                    comparison["eps_surprise_percent"].append(surprise_pct)
                    comparison["dates"].append(idx)
            
            return comparison
            
        except Exception as e:
            print(f"Error comparing estimates vs actual: {e}")
            return None
    
    def get_price_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Get historical price data
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with price data
        """
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period=period)
            return history
            
        except Exception as e:
            print(f"Error fetching price data: {e}")
            return None
