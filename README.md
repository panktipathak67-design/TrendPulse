📈 TrendPulse

AI-Powered Financial Research and Sentiment Analysis Platform

About the Project

TrendPulse is an AI-powered financial research platform designed to analyze stocks, ETFs, mutual funds, and financial news. It combines historical market data with sentiment analysis to help users understand market trends, compare financial assets, and study investment risks.

Features

- Stock Analysis: Analyze Indian and international stocks.
- ETF Analysis: Explore Indian and global ETFs.
- Mutual Fund Analysis: Search mutual funds and analyze historical NAV data.
- News & Sentiment Analysis: Analyze financial news using VADER sentiment analysis.
- Sentiment Classification: Classify news as Positive, Negative, or Neutral.
- Historical Charts: Visualize historical prices and NAV trends.
- Risk Analysis: Calculate volatility, Sharpe ratio, and maximum drawdown.
- Asset Comparison: Compare stocks, ETFs, and mutual funds.
- CSV Reports: Download analysis results for further research.

Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Yahoo Finance ("yfinance")
- Plotly
- VADER Sentiment
- Scikit-learn
- NewsAPI
- Mutual Fund NAV API

Installation

Clone the repository:

git clone https://github.com/YOUR-USERNAME/TrendPulse.git
cd TrendPulse

Install the required libraries:

pip install -r requirements.txt

Configuration

TrendPulse uses API keys for external services.

Set your NewsAPI key as an environment variable:

import os
os.environ["NEWS_API_KEY"] = "YOUR_NEWSAPI_KEY"

Do not upload API keys, passwords, or authentication tokens to GitHub.

Run the Application

Start the Streamlit application:

streamlit run app.py

The application will open in your browser.

Project Purpose

The main objective of TrendPulse is to explore how financial news sentiment and historical market information can be combined for financial research, asset comparison, and risk analysis.

Disclaimer

TrendPulse is developed for educational and research purposes only. It does not provide guaranteed predictions or personalized investment advice. Financial decisions should be made after independent research and consultation with qualified professionals.

Future Scope

- Improve sentiment analysis using advanced NLP models.
- Integrate additional financial data sources.
- Explore improved volatility forecasting methods.
- Add more financial indicators and analytical features.

---

Developed as an AI-based financial research project.
