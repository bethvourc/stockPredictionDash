import pandas as pd
import yfinance as yf
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import redis
from fastapi import BackgroundTasks
from datetime import datetime, timedelta

class SP500Service:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_expiry = 24 * 60 * 60  # 24 hours in seconds

    async def get_sp500_companies(self) -> list:
        """Fetch S&P 500 companies from Wikipedia and cache the results"""
        cached_data = self.redis_client.get('sp500_companies')
        if cached_data:
            return eval(cached_data)

        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()

        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', {'class': 'wikitable'})
        
        companies = []
        for row in table.findAll('tr')[1:]:
            cols = row.findAll('td')
            if len(cols) >= 4:
                company = {
                    'symbol': cols[0].text.strip(),
                    'name': cols[1].text.strip(),
                    'sector': cols[3].text.strip(),
                    'sub_industry': cols[4].text.strip() if len(cols) > 4 else ''
                }
                companies.append(company)

        # Cache the results
        self.redis_client.setex('sp500_companies', self.cache_expiry, str(companies))
        return companies

    async def get_sector_performance(self) -> dict:
        """Get performance metrics grouped by sector"""
        companies = await self.get_sp500_companies()
        sectors = {}
        
        for company in companies:
            sector = company['sector']
            if sector not in sectors:
                sectors[sector] = {
                    'count': 0,
                    'companies': [],
                    'performance': {'daily': 0, 'weekly': 0, 'monthly': 0, 'yearly': 0}
                }
            sectors[sector]['count'] += 1
            sectors[sector]['companies'].append(company['symbol'])

        return sectors

    async def update_stock_data(self, background_tasks: BackgroundTasks):
        """Update stock data for all S&P 500 companies"""
        companies = await self.get_sp500_companies()
        symbols = [company['symbol'] for company in companies]
        
        # Split symbols into chunks to avoid rate limiting
        chunk_size = 100
        symbol_chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]
        
        for chunk in symbol_chunks:
            background_tasks.add_task(self._update_chunk_data, chunk)

    async def _update_chunk_data(self, symbols: list):
        """Update data for a chunk of symbols"""
        data = yf.download(
            symbols,
            start=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d'),
            group_by='ticker'
        )
        
        for symbol in symbols:
            try:
                stock_data = data[symbol] if len(symbols) > 1 else data
                stock_data = stock_data.reset_index()
                self.redis_client.setex(
                    f'stock_data_{symbol}',
                    self.cache_expiry,
                    stock_data.to_json()
                )
            except Exception as e:
                print(f"Error updating data for {symbol}: {str(e)}")

    async def get_top_performers(self, timeframe: str = 'daily') -> list:
        """Get top performing stocks based on timeframe"""
        companies = await self.get_sp500_companies()
        performance_data = []
        
        for company in companies:
            symbol = company['symbol']
            cached_data = self.redis_client.get(f'stock_data_{symbol}')
            if cached_data:
                data = pd.read_json(cached_data)
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    if timeframe == 'daily':
                        change = (latest_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]
                    elif timeframe == 'weekly':
                        change = (latest_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]
                    elif timeframe == 'monthly':
                        change = (latest_price - data['Close'].iloc[-22]) / data['Close'].iloc[-22]
                    else:  # yearly
                        change = (latest_price - data['Close'].iloc[0]) / data['Close'].iloc[0]
                    
                    performance_data.append({
                        'symbol': symbol,
                        'name': company['name'],
                        'sector': company['sector'],
                        'change': change * 100,
                        'price': latest_price
                    })

        return sorted(performance_data, key=lambda x: x['change'], reverse=True)