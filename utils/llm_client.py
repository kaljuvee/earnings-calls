"""
LLM Client for Earnings Call Analysis
Integrates XAI and Gemini via LangChain
"""

import os
from typing import Optional, Dict, List
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph
from typing_extensions import TypedDict


class AnalysisState(TypedDict):
    """State for the analysis workflow"""
    ticker: str
    quarter: int
    year: int
    company_name: str
    transcript: str
    financial_context: str
    main_analysis: Optional[str]
    sentiment_analysis: Optional[str]
    comparison_analysis: Optional[str]
    predictive_signals: Optional[str]
    final_report: Optional[str]


class LLMClient:
    """Client for LLM-powered analysis using LangChain"""
    
    def __init__(self, provider: str = "xai", model: str = None):
        """
        Initialize LLM client
        
        Args:
            provider: 'xai' or 'gemini'
            model: Specific model name (optional)
        """
        self.provider = provider
        
        if provider == "xai":
            # XAI uses OpenAI-compatible API
            self.llm = ChatOpenAI(
                model=model or "grok-beta",
                api_key=os.getenv("XAI_API_KEY"),
                base_url="https://api.x.ai/v1",
                temperature=0.7
            )
        elif provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model or "gemini-pro",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def analyze_transcript(self, ticker: str, quarter: int, year: int,
                          transcript: str, company_name: str = "",
                          financial_context: str = "") -> str:
        """
        Analyze earnings call transcript using the main analysis template
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number
            year: Year
            transcript: Full transcript text
            company_name: Company name
            financial_context: Additional financial context
            
        Returns:
            Structured analysis text
        """
        from prompts.analysis_prompt import ANALYSIS_TEMPLATE
        
        prompt = PromptTemplate(
            input_variables=["ticker", "quarter", "year", "company_name", 
                           "transcript", "financial_context"],
            template=ANALYSIS_TEMPLATE
        )
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "ticker": ticker,
            "quarter": quarter,
            "year": year,
            "company_name": company_name,
            "transcript": transcript[:50000],  # Limit to avoid token limits
            "financial_context": financial_context
        })
        
        return result.content
    
    def analyze_sentiment(self, transcript: str) -> str:
        """
        Analyze sentiment and tone of the transcript
        
        Args:
            transcript: Full transcript text
            
        Returns:
            Sentiment analysis
        """
        from prompts.analysis_prompt import SENTIMENT_ANALYSIS_TEMPLATE
        
        prompt = PromptTemplate(
            input_variables=["transcript"],
            template=SENTIMENT_ANALYSIS_TEMPLATE
        )
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "transcript": transcript[:30000]
        })
        
        return result.content
    
    def compare_estimates_vs_actual(self, ticker: str, quarter: int, year: int,
                                   estimates: str, actual_results: str) -> str:
        """
        Compare analyst estimates with actual results
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number
            year: Year
            estimates: Analyst estimates data
            actual_results: Actual results from transcript
            
        Returns:
            Comparison analysis
        """
        from prompts.analysis_prompt import FINANCIAL_COMPARISON_TEMPLATE
        
        prompt = PromptTemplate(
            input_variables=["ticker", "quarter", "year", "estimates", "actual_results"],
            template=FINANCIAL_COMPARISON_TEMPLATE
        )
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "ticker": ticker,
            "quarter": quarter,
            "year": year,
            "estimates": estimates,
            "actual_results": actual_results
        })
        
        return result.content
    
    def generate_predictive_signals(self, analysis_summary: str, 
                                   financial_data: str) -> str:
        """
        Generate predictive signals for future stock performance
        
        Args:
            analysis_summary: Summary of the analysis
            financial_data: Financial data and metrics
            
        Returns:
            Predictive signals analysis
        """
        from prompts.analysis_prompt import PREDICTIVE_SIGNAL_TEMPLATE
        
        prompt = PromptTemplate(
            input_variables=["analysis_summary", "financial_data"],
            template=PREDICTIVE_SIGNAL_TEMPLATE
        )
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "analysis_summary": analysis_summary,
            "financial_data": financial_data
        })
        
        return result.content
    
    def run_agentic_analysis(self, ticker: str, quarter: int, year: int,
                            transcript: str, company_name: str = "",
                            financial_context: str = "") -> Dict[str, str]:
        """
        Run complete agentic analysis workflow using LangGraph
        
        Args:
            ticker: Stock ticker symbol
            quarter: Quarter number
            year: Year
            transcript: Full transcript text
            company_name: Company name
            financial_context: Additional financial context
            
        Returns:
            Dictionary with all analysis components
        """
        # Define the workflow
        workflow = StateGraph(AnalysisState)
        
        # Define nodes (analysis steps)
        def main_analysis_node(state: AnalysisState) -> AnalysisState:
            """Generate main earnings analysis"""
            analysis = self.analyze_transcript(
                state["ticker"], state["quarter"], state["year"],
                state["transcript"], state["company_name"],
                state["financial_context"]
            )
            state["main_analysis"] = analysis
            return state
        
        def sentiment_analysis_node(state: AnalysisState) -> AnalysisState:
            """Analyze sentiment"""
            sentiment = self.analyze_sentiment(state["transcript"])
            state["sentiment_analysis"] = sentiment
            return state
        
        def predictive_signals_node(state: AnalysisState) -> AnalysisState:
            """Generate predictive signals"""
            signals = self.generate_predictive_signals(
                state["main_analysis"] or "",
                state["financial_context"]
            )
            state["predictive_signals"] = signals
            return state
        
        def compile_report_node(state: AnalysisState) -> AnalysisState:
            """Compile final report"""
            report = f"""# Earnings Call Analysis Report
            
{state["main_analysis"]}

---

## Sentiment Analysis

{state["sentiment_analysis"]}

---

## Predictive Signals

{state["predictive_signals"]}
"""
            state["final_report"] = report
            return state
        
        # Add nodes to workflow
        workflow.add_node("main_analysis", main_analysis_node)
        workflow.add_node("sentiment_analysis", sentiment_analysis_node)
        workflow.add_node("predictive_signals", predictive_signals_node)
        workflow.add_node("compile_report", compile_report_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("main_analysis")
        workflow.add_edge("main_analysis", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", "predictive_signals")
        workflow.add_edge("predictive_signals", "compile_report")
        workflow.set_finish_point("compile_report")
        
        # Compile and run
        app = workflow.compile()
        
        initial_state: AnalysisState = {
            "ticker": ticker,
            "quarter": quarter,
            "year": year,
            "company_name": company_name,
            "transcript": transcript,
            "financial_context": financial_context,
            "main_analysis": None,
            "sentiment_analysis": None,
            "comparison_analysis": None,
            "predictive_signals": None,
            "final_report": None
        }
        
        # Run the workflow
        final_state = app.invoke(initial_state)
        
        return {
            "main_analysis": final_state.get("main_analysis", ""),
            "sentiment_analysis": final_state.get("sentiment_analysis", ""),
            "predictive_signals": final_state.get("predictive_signals", ""),
            "final_report": final_state.get("final_report", "")
        }
