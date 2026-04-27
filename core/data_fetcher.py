import yfinance as yf
from ddgs import DDGS

def get_suggested_companies():
    """Daftar emiten target untuk audit ESG."""
    return [
        {"ticker": "BP", "name": "BP p.l.c. (Oil & Gas)"},
        {"ticker": "XOM", "name": "Exxon Mobil (Oil & Gas)"},
        {"ticker": "HMB", "name": "H&M (Fast Fashion)"},
        {"ticker": "NSRGY", "name": "Nestle (Consumer Goods)"},
        {"ticker": "GOTO.JK", "name": "GoTo Gojek Tokopedia (Tech)"},
        {"ticker": "UNVR.JK", "name": "Unilever Indonesia (FMCG)"}
    ]

def get_company_profile(ticker: str) -> dict:
    """Mengambil profil lengkap beserta website untuk ekstrak logo."""
    try:
        info = yf.Ticker(ticker).info
        # Mengambil domain website untuk clearbit logo API
        website = info.get('website', '')
        domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0] if website else ''
        logo_url = f"https://logo.clearbit.com/{domain}" if domain else ""
        
        return {
            "name": info.get('longName', ticker),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "logo": logo_url
        }
    except Exception as e:
        print(f"[SYS_WARN] Data profil {ticker} gagal ditarik: {e}")
        return {"name": ticker, "sector": "N/A", "industry": "N/A", "logo": ""}

def fetch_esg_news(company_name: str, max_results: int = 7) -> list:
    """Menyedot berita investigasi."""
    query = f'"{company_name}" AND (environment OR pollution OR scandal OR lawsuit OR "waste management" OR greenwashing OR emissions OR corruption)'
    news_data = []
    
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results, safesearch='off')
            for r in results:
                news_data.append({
                    "title": r.get("title", "Unknown Title"),
                    "body": r.get("body", "No content available."),
                    "source": r.get("href", "#")
                })
        
        if not news_data:
            return [{"title": "CLEAN RECORD", "body": "No recent controversies found.", "source": ""}]
        return news_data
    except Exception as e:
        return [{"title": "API ERROR", "body": f"Failed to fetch: {str(e)}", "source": ""}]