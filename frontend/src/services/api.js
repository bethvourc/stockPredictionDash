import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const searchStocks = async (query) => {
    const response = await axios.get(`${API_URL}/stocks/search?query=${query}`);
    return response.data;
};

export const fetchStockData = async (ticker) => {
    const response = await axios.get(`${API_URL}/stocks/stock/${ticker}`);
    return response.data;
};

export const fetchSectorData = async () => {
    const response = await axios.get(`${API_URL}/sp500/sectors`);
    return response.data;
};

export const fetchTopPerformers = async (timeframe) => {
    const response = await axios.get(`${API_URL}/sp500/top-performers?timeframe=${timeframe}`);
    return response.data;
};

export const fetchForecast = async (ticker, years, confidenceInterval) => {
    const response = await axios.get(
        `${API_URL}/stocks/forecast/${ticker}?years=${years}&confidence_interval=${confidenceInterval}`
    );
    return response.data;
};