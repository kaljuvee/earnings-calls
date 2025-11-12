"""
Data Correlation Utility
Correlates earnings call analysis with financial data from Yahoo Finance
"""

import pandas as pd
from typing import Dict, Optional, List
from utils.yfinance_client import YFinanceClient
import json


class DataCorrelator:
    """Correlates earnings analysis with financial data"""
    
    def __init__(self):
        """Initialize data correlator"""
        self.yf_client = YFinanceClient()
    
    def get_financial_summary(self, ticker: str) -> Dict:
        """
        Get comprehensive financial summary for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with financial summary data
        """
        summary = {
            "company_info": {},
            "analyst_estimates": {},
            "earnings_history": {},
            "recommendations": {},
            "price_data": {}
        }
        
        # Get company info
        info = self.yf_client.get_company_info(ticker)
        if info:
            summary["company_info"] = {
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "employees": info.get("fullTimeEmployees", 0)
            }
        
        # Get analyst estimates
        estimates = self.yf_client.get_analyst_estimates(ticker)
        if estimates:
            summary["analyst_estimates"] = estimates
        
        # Get earnings history
        earnings = self.yf_client.get_earnings_data(ticker)
        if earnings is not None and not earnings.empty:
            summary["earnings_history"] = earnings.head(10).to_dict()
        
        # Get recommendations
        recommendations = self.yf_client.get_analyst_recommendations(ticker)
        if recommendations is not None and not recommendations.empty:
            summary["recommendations"] = recommendations.head(20).to_dict()
        
        # Get recent price data
        prices = self.yf_client.get_price_data(ticker, period="3mo")
        if prices is not None and not prices.empty:
            summary["price_data"] = {
                "current_price": float(prices['Close'].iloc[-1]),
                "high_3mo": float(prices['High'].max()),
                "low_3mo": float(prices['Low'].min()),
                "avg_volume_3mo": float(prices['Volume'].mean())
            }
        
        return summary
    
    def compare_estimates_with_actuals(self, ticker: str, 
                                      actual_results: Dict) -> Dict:
        """
        Compare analyst estimates with actual results
        
        Args:
            ticker: Stock ticker symbol
            actual_results: Dictionary with actual results from transcript
            
        Returns:
            Comparison analysis
        """
        comparison = self.yf_client.compare_estimates_vs_actual(ticker)
        
        if not comparison:
            return {}
        
        # Calculate summary statistics
        if comparison.get("eps_surprise_percent"):
            surprises = comparison["eps_surprise_percent"]
            avg_surprise = sum(surprises) / len(surprises) if surprises else 0
            
            return {
                "comparison_data": comparison,
                "average_surprise_pct": avg_surprise,
                "beat_rate": sum(1 for s in surprises if s > 0) / len(surprises) if surprises else 0,
                "latest_surprise": surprises[0] if surprises else 0
            }
        
        return {"comparison_data": comparison}
    
    def generate_financial_context(self, ticker: str, quarter: int, 
                                   year: int) -> str:
        """
        Generate financial context string for LLM analysis
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number
            year: Year
            
        Returns:
            Formatted financial context string
        """
        summary = self.get_financial_summary(ticker)
        
        context_parts = []
        
        # Company info
        if summary.get("company_info"):
            info = summary["company_info"]
            context_parts.append(f"Company: {info.get('name', ticker)}")
            context_parts.append(f"Sector: {info.get('sector', 'N/A')}")
            context_parts.append(f"Industry: {info.get('industry', 'N/A')}")
            if info.get('market_cap'):
                market_cap_b = info['market_cap'] / 1e9
                context_parts.append(f"Market Cap: ${market_cap_b:.2f}B")
        
        # Analyst estimates
        if summary.get("analyst_estimates"):
            estimates = summary["analyst_estimates"]
            if estimates.get("earnings_estimate"):
                context_parts.append("\nAnalyst Earnings Estimates:")
                context_parts.append(json.dumps(estimates["earnings_estimate"], indent=2))
            if estimates.get("revenue_estimate"):
                context_parts.append("\nAnalyst Revenue Estimates:")
                context_parts.append(json.dumps(estimates["revenue_estimate"], indent=2))
        
        # Recent recommendations
        if summary.get("recommendations"):
            context_parts.append("\nRecent Analyst Recommendations:")
            recs = summary["recommendations"]
            context_parts.append(json.dumps(recs, indent=2)[:500])  # Limit size
        
        # Price data
        if summary.get("price_data"):
            price = summary["price_data"]
            context_parts.append(f"\nRecent Price Data:")
            context_parts.append(f"Current Price: ${price.get('current_price', 0):.2f}")
            context_parts.append(f"3-Month High: ${price.get('high_3mo', 0):.2f}")
            context_parts.append(f"3-Month Low: ${price.get('low_3mo', 0):.2f}")
        
        return "\n".join(context_parts)
    
    def calculate_surprise_metrics(self, ticker: str) -> Dict:
        """
        Calculate earnings surprise metrics
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with surprise metrics
        """
        comparison = self.yf_client.compare_estimates_vs_actual(ticker)
        
        if not comparison or not comparison.get("eps_surprise_percent"):
            return {}
        
        surprises = comparison["eps_surprise_percent"]
        
        return {
            "average_surprise": sum(surprises) / len(surprises) if surprises else 0,
            "median_surprise": sorted(surprises)[len(surprises)//2] if surprises else 0,
            "max_surprise": max(surprises) if surprises else 0,
            "min_surprise": min(surprises) if surprises else 0,
            "beat_count": sum(1 for s in surprises if s > 0),
            "miss_count": sum(1 for s in surprises if s < 0),
            "meet_count": sum(1 for s in surprises if s == 0),
            "total_quarters": len(surprises)
        }
    
    def get_recommendation_summary(self, ticker: str) -> Dict:
        """
        Get summary of analyst recommendations
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with recommendation summary
        """
        recommendations = self.yf_client.get_analyst_recommendations(ticker)
        
        if recommendations is None or recommendations.empty:
            return {}
        
        # Get most recent recommendations
        recent = recommendations.head(20)
        
        # Count by grade
        grade_counts = recent['To Grade'].value_counts().to_dict() if 'To Grade' in recent.columns else {}
        
        return {
            "total_recommendations": len(recent),
            "grade_distribution": grade_counts,
            "most_recent_date": str(recent.index[0]) if len(recent) > 0 else "",
            "firms_covering": recent['Firm'].nunique() if 'Firm' in recent.columns else 0
        }
    
    def generate_correlation_report(self, ticker: str, quarter: int, 
                                   year: int, analysis: str) -> str:
        """
        Generate comprehensive correlation report
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number
            year: Year
            analysis: LLM analysis text
            
        Returns:
            Formatted correlation report
        """
        summary = self.get_financial_summary(ticker)
        surprise_metrics = self.calculate_surprise_metrics(ticker)
        rec_summary = self.get_recommendation_summary(ticker)
        
        report_parts = [
            f"# Financial Data Correlation Report",
            f"## {ticker} - Q{quarter} {year}\n",
            "---\n"
        ]
        
        # Company overview
        if summary.get("company_info"):
            info = summary["company_info"]
            report_parts.append("## Company Overview\n")
            report_parts.append(f"**Name:** {info.get('name', ticker)}")
            report_parts.append(f"**Sector:** {info.get('sector', 'N/A')}")
            report_parts.append(f"**Industry:** {info.get('industry', 'N/A')}")
            if info.get('market_cap'):
                market_cap_b = info['market_cap'] / 1e9
                report_parts.append(f"**Market Cap:** ${market_cap_b:.2f}B")
            report_parts.append("\n---\n")
        
        # Surprise metrics
        if surprise_metrics:
            report_parts.append("## Historical Earnings Surprise Metrics\n")
            report_parts.append(f"**Average Surprise:** {surprise_metrics.get('average_surprise', 0):.2f}%")
            report_parts.append(f"**Beat Rate:** {surprise_metrics.get('beat_count', 0)}/{surprise_metrics.get('total_quarters', 0)} quarters")
            report_parts.append(f"**Max Surprise:** {surprise_metrics.get('max_surprise', 0):.2f}%")
            report_parts.append(f"**Min Surprise:** {surprise_metrics.get('min_surprise', 0):.2f}%")
            report_parts.append("\n---\n")
        
        # Analyst recommendations
        if rec_summary:
            report_parts.append("## Analyst Recommendations\n")
            report_parts.append(f"**Total Recent Recommendations:** {rec_summary.get('total_recommendations', 0)}")
            report_parts.append(f"**Firms Covering:** {rec_summary.get('firms_covering', 0)}")
            if rec_summary.get('grade_distribution'):
                report_parts.append("\n**Grade Distribution:**")
                for grade, count in rec_summary['grade_distribution'].items():
                    report_parts.append(f"- {grade}: {count}")
            report_parts.append("\n---\n")
        
        # Price data
        if summary.get("price_data"):
            price = summary["price_data"]
            report_parts.append("## Recent Price Performance\n")
            report_parts.append(f"**Current Price:** ${price.get('current_price', 0):.2f}")
            report_parts.append(f"**3-Month High:** ${price.get('high_3mo', 0):.2f}")
            report_parts.append(f"**3-Month Low:** ${price.get('low_3mo', 0):.2f}")
            report_parts.append(f"**Average Volume (3mo):** {price.get('avg_volume_3mo', 0):,.0f}")
            report_parts.append("\n---\n")
        
        return "\n".join(report_parts)
