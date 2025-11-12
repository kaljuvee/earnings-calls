"""
Earnings Call Analysis Prompt Templates
"""

ANALYSIS_TEMPLATE = """
You are an expert financial analyst specializing in earnings call analysis. Your task is to analyze the following earnings call transcript and provide a comprehensive, structured analysis.

**Transcript Information:**
- Ticker: {ticker}
- Quarter: Q{quarter} {year}
- Company: {company_name}

**Transcript:**
{transcript}

**Financial Context (if available):**
{financial_context}

---

Please provide a detailed analysis following this exact structure:

# ${ticker} Q{quarter} {year} earnings: [One-line summary with key highlights]

[Opening paragraph: 2-3 sentences summarizing the overall quarter performance, key metrics, guidance changes, and major strategic announcements]

## 🐂 𝗧𝗵𝗲 𝗕𝘂𝗹𝗹 𝗖𝗮𝘀𝗲

[2-3 paragraphs explaining the strongest positive arguments for the stock. Focus on:
- Revenue and earnings growth metrics with YoY comparisons
- Margin improvements or high-margin revenue growth
- Strategic initiatives and partnerships
- Market expansion and competitive advantages
- Raised guidance or positive outlook changes]

## 🐻 𝗧𝗵𝗲 𝗕𝗲𝗮𝗿 𝗖𝗮𝘀𝗲

[2-3 paragraphs explaining the key concerns and risks. Focus on:
- Rising costs or margin compression
- Slowing growth rates
- Increased competition or market challenges
- Execution risks
- Guidance concerns or uncertainties]

## ⚖️ 𝗩𝗲𝗿𝗱𝗶𝗰𝘁

[1-2 paragraphs providing your balanced assessment. Which case is more compelling and why? Consider both near-term and long-term perspectives. Be specific about what would need to change for the opposite case to become more compelling.]

---

## 𝗧𝗵𝗲𝗺𝗲𝘀, 𝗗𝗿𝗶𝘃𝗲𝗿𝘀, 𝗮𝗻𝗱 𝗖𝗼𝗻𝗰𝗲𝗿𝗻𝘀

[Identify 4-6 key themes. For each theme, use an emoji indicator and format as follows:]

🟢 **[Positive Theme Title]**: [2-3 sentences explaining the theme, its significance, and how it evolved from previous quarters if applicable]

🟡 **[Neutral/Mixed Theme Title]**: [2-3 sentences explaining the theme and why it's neither clearly positive nor negative]

🔴 **[Negative Theme Title]**: [2-3 sentences explaining the concern and its potential impact]

⚪ **[New/Emerging Theme Title]**: [2-3 sentences explaining new developments or strategic initiatives]

---

## 𝗠𝗮𝗶𝗻 𝗙𝗶𝗻𝗮𝗻𝗰𝗶𝗮𝗹𝘀 (𝗤{quarter} {year})

[List 6-10 key financial metrics in bullet format with YoY comparisons:]

* **Total Revenue**: $XXX, up/down X% YoY
* **[Key Metric]**: $XXX, up/down X% YoY
* **Net Income**: $XXX, up/down X% YoY [Note any one-time items]
* **[Margin Metric]**: X%, compared to X% in Q{quarter} {prev_year}
* **[Key Operating Metric]**: XXX, up/down X% YoY
* **[Other Important Metrics]**: ...

---

## 𝗚𝘂𝗶𝗱𝗮𝗻𝗰𝗲 (𝗙𝘂𝗹𝗹 𝗬𝗲𝗮𝗿 {year})

[List guidance items with emoji indicators:]

🟢 **[Metric Raised]**: Raised to $XXX - $XXX, from prior $XXX - $XXX. [Brief explanation of significance]

🔴 **[Metric Lowered/Concern]**: [Description and explanation]

⚪ **[Metric Maintained]**: [Description]

---

## 𝗠𝗮𝗶𝗻 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻𝘀 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗘𝗮𝗿𝗻𝗶𝗻𝗴𝘀 𝗖𝗮𝗹𝗹

[List 4-6 thoughtful, specific questions that investors should want answered:]

1. **[Question Category]**: [Specific question about strategy, metrics, or outlook]
2. **[Question Category]**: [Question about competitive dynamics or market trends]
3. **[Question Category]**: [Question about financial sustainability or margins]
4. **[Question Category]**: [Question about execution or risks]

---

**Analysis Guidelines:**
- Be specific with numbers and percentages
- Always include YoY comparisons where possible
- Highlight any one-time items or adjustments
- Compare guidance changes to previous quarters
- Focus on forward-looking implications
- Maintain objectivity while being insightful
- Use the exact formatting shown above including emojis and bold text
"""

FINANCIAL_COMPARISON_TEMPLATE = """
You are analyzing the relationship between analyst estimates and actual earnings results.

**Company:** {ticker}
**Quarter:** Q{quarter} {year}

**Analyst Estimates:**
{estimates}

**Actual Results (from transcript):**
{actual_results}

**Task:**
Compare the analyst estimates with the actual results and provide:

1. **Beat/Miss Analysis**: For each key metric (EPS, Revenue, etc.), did the company beat, meet, or miss expectations? By how much (absolute and percentage)?

2. **Surprise Factors**: What were the biggest positive and negative surprises relative to expectations?

3. **Guidance vs Estimates**: How does the company's guidance compare to current analyst estimates for future quarters?

4. **Market Implications**: Based on the magnitude and direction of surprises, what might be the likely market reaction?

Format your response as a structured analysis with clear sections and specific numbers.
"""

SENTIMENT_ANALYSIS_TEMPLATE = """
Analyze the sentiment and tone of this earnings call transcript.

**Transcript:**
{transcript}

Provide:
1. **Overall Sentiment Score** (1-10, where 1 is very negative and 10 is very positive)
2. **Management Confidence Level** (Low/Medium/High)
3. **Key Sentiment Indicators**: Specific phrases or statements that reveal sentiment
4. **Tone Shifts**: Any notable changes in tone during the call
5. **Forward-Looking Sentiment**: How optimistic or cautious is management about the future?

Be specific and quote relevant passages to support your assessment.
"""

PREDICTIVE_SIGNAL_TEMPLATE = """
Based on the earnings call analysis, identify potential predictive signals for future stock performance.

**Analysis Summary:**
{analysis_summary}

**Financial Data:**
{financial_data}

Provide:

1. **Short-term Signals (1-30 days)**:
   - Likely immediate market reaction
   - Key catalysts or concerns
   - Momentum indicators

2. **Medium-term Signals (1-6 months)**:
   - Fundamental trajectory
   - Competitive positioning
   - Execution risks/opportunities

3. **Predictive Score** (1-10):
   - 1-3: Strong negative signals
   - 4-6: Mixed/neutral signals
   - 7-10: Strong positive signals

4. **Key Metrics to Watch**: What specific metrics or events would confirm or invalidate your prediction?

Be specific and data-driven in your assessment.
"""
