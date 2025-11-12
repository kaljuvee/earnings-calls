"""
Sample Transcript Generator
Generates realistic earnings call transcripts for demonstration purposes
"""

import random
from datetime import datetime
from typing import Dict, List

class SampleTranscriptGenerator:
    """Generate sample earnings call transcripts"""
    
    # Sample companies with realistic data
    COMPANIES = {
        'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
        'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology'},
        'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
        'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical'},
        'TSLA': {'name': 'Tesla Inc.', 'sector': 'Automotive'},
        'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
        'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
        'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
        'V': {'name': 'Visa Inc.', 'sector': 'Financial Services'},
        'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Defensive'}
    }
    
    def generate_transcript(self, ticker: str, year: int, quarter: int) -> str:
        """
        Generate a sample earnings call transcript
        
        Args:
            ticker: Stock ticker symbol
            year: Year of earnings call
            quarter: Quarter number (1-4)
        
        Returns:
            Formatted markdown transcript
        """
        company = self.COMPANIES.get(ticker.upper(), {'name': f'{ticker} Inc.', 'sector': 'Technology'})
        
        # Generate realistic financial metrics
        revenue = random.randint(50, 500) * 1000000000  # $50B - $500B
        revenue_growth = random.uniform(5, 35)  # 5% - 35% growth
        eps = round(random.uniform(1.0, 5.0), 2)
        eps_estimate = round(eps * random.uniform(0.90, 0.98), 2)
        
        # Quarter dates
        quarter_months = {1: 'March', 2: 'June', 3: 'September', 4: 'December'}
        quarter_month = quarter_months[quarter]
        
        transcript = f"""# {company['name']} ({ticker}) Q{quarter} {year} Earnings Call Transcript

**Date:** {quarter_month} {random.randint(1, 28)}, {year}  
**Company:** {company['name']}  
**Ticker:** {ticker}  
**Quarter:** Q{quarter} {year}  
**Sector:** {company['sector']}

---

## Operator

Good afternoon, and welcome to {company['name']}'s Q{quarter} {year} Earnings Conference Call. Today's call is being recorded. At this time, I would like to turn the call over to the Vice President of Investor Relations. Please go ahead.

## Vice President, Investor Relations

Thank you. Good afternoon, and welcome to {company['name']}'s earnings conference call for the {quarter_month} quarter of fiscal {year}. With me today are our CEO and CFO.

Before we begin, I'd like to remind you that some of the statements we make today may be considered forward-looking and involve risks and uncertainties. Actual results may differ materially from those projected in any forward-looking statements. Please refer to our recent filings with the SEC for more information on risk factors that could cause actual results to differ.

With that, I'll turn it over to our CEO.

## Chief Executive Officer

Thank you, and good afternoon, everyone. I'm pleased to report another strong quarter for {company['name']}. Our Q{quarter} results demonstrate the strength of our business model and the continued execution of our strategic initiatives.

### Financial Highlights

For Q{quarter} {year}, we achieved:

- **Total Revenue:** ${revenue / 1000000000:.1f} billion, up {revenue_growth:.1f}% year-over-year
- **Earnings Per Share:** ${eps}, exceeding analyst estimates of ${eps_estimate}
- **Operating Margin:** {random.randint(25, 45)}%, reflecting our operational efficiency
- **Cash Flow from Operations:** ${random.randint(20, 80)} billion

### Key Business Drivers

Our strong performance this quarter was driven by several factors:

**1. Product Innovation**  
We continue to invest heavily in R&D, with several new product launches this quarter that have been well-received by customers. Our innovation pipeline remains robust, and we're excited about upcoming releases.

**2. Market Expansion**  
We've successfully expanded into new geographic markets, with particularly strong growth in emerging markets. International revenue now represents {random.randint(40, 60)}% of total revenue.

**3. Digital Transformation**  
Our digital initiatives continue to gain traction. Cloud services revenue grew {random.randint(20, 50)}% year-over-year, and we're seeing strong adoption across all customer segments.

**4. Operational Excellence**  
We've made significant progress in improving operational efficiency. Supply chain optimization and automation initiatives have contributed to margin expansion.

### Strategic Initiatives

Looking ahead, we remain focused on three key strategic priorities:

1. **Innovation Leadership:** Continuing to invest in cutting-edge technologies including AI, machine learning, and next-generation products
2. **Customer Experience:** Enhancing our customer engagement platforms and support services
3. **Sustainable Growth:** Expanding our addressable market while maintaining disciplined capital allocation

### Market Outlook

The overall market environment remains dynamic. While we're seeing some macroeconomic headwinds, demand for our products and services remains strong. We're well-positioned to navigate any near-term challenges while capitalizing on long-term growth opportunities.

With that, I'll turn it over to our CFO to discuss the financial details.

## Chief Financial Officer

Thank you. I'll provide more detail on our Q{quarter} financial performance and outlook.

### Revenue Analysis

Total revenue of ${revenue / 1000000000:.1f} billion increased {revenue_growth:.1f}% year-over-year, driven by:

- **Product Revenue:** ${revenue * 0.6 / 1000000000:.1f} billion, up {random.randint(8, 20)}% YoY
- **Services Revenue:** ${revenue * 0.4 / 1000000000:.1f} billion, up {random.randint(15, 35)}% YoY

Services revenue continues to be a key growth driver, now representing {40}% of total revenue, up from {35}% in the prior year period.

### Profitability Metrics

- **Gross Margin:** {random.randint(38, 48)}%, up {random.randint(50, 200)} basis points YoY
- **Operating Margin:** {random.randint(25, 35)}%, reflecting strong operational leverage
- **Net Income:** ${revenue * 0.20 / 1000000000:.1f} billion
- **Diluted EPS:** ${eps}

The improvement in gross margin was primarily due to favorable product mix, operational efficiencies, and leverage on our fixed cost base.

### Balance Sheet and Cash Flow

We maintain a strong financial position:

- **Cash and Marketable Securities:** ${random.randint(100, 300)} billion
- **Operating Cash Flow:** ${random.randint(20, 80)} billion
- **Free Cash Flow:** ${random.randint(18, 75)} billion
- **Capital Returned to Shareholders:** ${random.randint(10, 40)} billion through dividends and buybacks

### Guidance

For Q{quarter + 1 if quarter < 4 else 1} {year if quarter < 4 else year + 1}, we expect:

- **Revenue:** ${revenue * random.uniform(1.02, 1.12) / 1000000000:.1f} billion to ${revenue * random.uniform(1.13, 1.20) / 1000000000:.1f} billion
- **Operating Margin:** {random.randint(26, 36)}% to {random.randint(27, 37)}%
- **EPS:** ${round(eps * random.uniform(1.05, 1.15), 2)} to ${round(eps * random.uniform(1.16, 1.25), 2)}

This guidance reflects our confidence in the business while acknowledging some near-term uncertainties in the macro environment.

### Capital Allocation

We remain committed to our balanced capital allocation strategy:

1. Investing in growth opportunities and R&D
2. Maintaining a strong balance sheet
3. Returning capital to shareholders through dividends and share repurchases

We're announcing a {random.randint(5, 15)}% increase in our quarterly dividend, reflecting our confidence in future cash generation.

With that, I'll turn it back to the operator for Q&A.

## Operator

Thank you. We will now begin the question-and-answer session. Our first question comes from an analyst at Goldman Sachs.

## Analyst - Goldman Sachs

Thank you for taking my question. Can you provide more color on the growth drivers for services revenue? And how should we think about the sustainability of this growth rate going forward?

## Chief Executive Officer

Great question. Services revenue growth is being driven by several factors. First, we're seeing strong adoption of our cloud platform, with enterprise customers increasingly migrating workloads. Second, our subscription services continue to gain traction across both consumer and enterprise segments. Third, we're benefiting from the growing installed base of our products, which drives recurring services revenue.

In terms of sustainability, we believe services can continue to grow in the {random.randint(20, 35)}% range for the foreseeable future. The market opportunity is large, our competitive position is strong, and we're continuing to invest in new services offerings.

## Chief Financial Officer

I'll add that services also have attractive unit economics with higher margins than our product business. As services become a larger percentage of the mix, we expect continued margin expansion.

## Analyst - Goldman Sachs

That's helpful. As a follow-up, can you discuss your AI strategy and how you're thinking about AI investments?

## Chief Executive Officer

AI is a core focus for us. We're investing significantly across multiple dimensions. First, we're integrating AI capabilities into our existing products to enhance user experience. Second, we're developing new AI-powered products and services. Third, we're using AI internally to improve operational efficiency.

We believe AI represents a generational opportunity, and we're well-positioned given our technology infrastructure, data assets, and talent. You'll see continued innovation from us in this area, and we expect AI to be a meaningful revenue driver over the next several years.

## Operator

Our next question comes from an analyst at Morgan Stanley.

## Analyst - Morgan Stanley

Thanks for the question. Can you discuss the competitive environment and how you're maintaining market share?

## Chief Executive Officer

The competitive environment remains intense, but we're confident in our competitive position. Our differentiation comes from several factors: superior product quality, strong brand loyalty, integrated ecosystem, and continuous innovation.

We're seeing market share gains in several key categories. Our focus remains on delivering exceptional customer value rather than competing solely on price. This strategy has served us well and positions us for sustainable long-term growth.

## Analyst - Morgan Stanley

And as a follow-up, how are you thinking about M&A opportunities?

## Chief Financial Officer

We maintain a disciplined approach to M&A. We're always evaluating opportunities that can accelerate our strategic priorities, whether that's technology acquisition, talent, or market expansion. However, we have a high bar for acquisitions – they need to be strategically aligned, financially attractive, and culturally compatible.

That said, organic investment remains our primary focus. We believe we have significant opportunities to drive growth through internal innovation and market expansion.

## Operator

Our next question comes from an analyst at JPMorgan.

## Analyst - JPMorgan

Thank you. Can you provide an update on your international expansion, particularly in emerging markets?

## Chief Executive Officer

International expansion remains a key priority. We're seeing particularly strong growth in Asia-Pacific and Latin America. In emerging markets, we're taking a localized approach – adapting our products and go-to-market strategies to local needs and preferences.

We're also investing in local partnerships, distribution channels, and customer support infrastructure. While emerging markets currently represent about {random.randint(15, 25)}% of revenue, we see significant long-term potential as these markets mature.

## Analyst - JPMorgan

And how should we think about the margin profile of international business versus domestic?

## Chief Financial Officer

International margins are currently below our domestic margins, primarily due to investment phase dynamics and market-specific factors. However, we're seeing steady margin improvement as we scale. Long-term, we expect international margins to converge with domestic margins as we achieve greater operating leverage.

## Operator

That concludes our Q&A session. I'll now turn the call back to management for closing remarks.

## Chief Executive Officer

Thank you all for joining us today. In summary, Q{quarter} was another strong quarter that demonstrates the resilience of our business model and the execution of our strategic initiatives. We're well-positioned for continued growth, and we remain focused on creating long-term value for our shareholders.

We appreciate your continued support and look forward to updating you on our progress next quarter. Thank you.

## Operator

This concludes today's conference call. Thank you for participating. You may now disconnect.

---

**Disclaimer:** This is a sample transcript generated for demonstration purposes. It does not represent actual earnings call content.
"""
        return transcript
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available sample tickers"""
        return list(self.COMPANIES.keys())
    
    def get_company_info(self, ticker: str) -> Dict:
        """Get company information"""
        return self.COMPANIES.get(ticker.upper(), {})


def generate_sample_transcript(ticker: str, year: int, quarter: int) -> str:
    """Helper function to generate sample transcript"""
    generator = SampleTranscriptGenerator()
    return generator.generate_transcript(ticker, year, quarter)


if __name__ == "__main__":
    # Test the generator
    generator = SampleTranscriptGenerator()
    transcript = generator.generate_transcript('AAPL', 2024, 4)
    print(transcript[:1000])  # Print first 1000 characters
    print(f"\n... (Total length: {len(transcript)} characters)")
