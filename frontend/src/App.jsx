import React, { useState, useEffect } from 'react';
import { fetchStockData, fetchSectorData, fetchTopPerformers } from './services/api';
import CompanyInfo from './components/CompanyInfo';
import TechnicalChart from './components/TechnicalChart';
import ForecastChart from './components/ForecastChart';
import ModelMetrics from './components/ModelMetrics';
import Sidebar from './components/Sidebar';
import SectorOverview from './components/SectorOverview';
import TopPerformers from './components/TopPerformers';
import StockSearch from './components/StockSearch';
import LoadingSpinner from './components/LoadingSpinner';

const App = () => {
    const [selectedStock, setSelectedStock] = useState('AAPL');
    const [years, setYears] = useState(1);
    const [confidenceInterval, setConfidenceInterval] = useState(90);
    const [stockData, setStockData] = useState(null);
    const [forecastData, setForecastData] = useState(null);
    const [sectorData, setSectorData] = useState(null);
    const [topPerformers, setTopPerformers] = useState(null);
    const [timeframe, setTimeframe] = useState('daily');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const [stockResponse, sectorResponse, performersResponse] = await Promise.all([
                    fetchStockData(selectedStock),
                    fetchSectorData(),
                    fetchTopPerformers(timeframe)
                ]);
                setStockData(stockResponse);
                setSectorData(sectorResponse);
                setTopPerformers(performersResponse);
            } catch (error) {
                setError('Error loading data: ' + error.message);
                console.error('Error loading data:', error);
            }
            setLoading(false);
        };

        loadData();
    }, [selectedStock, timeframe]);

    if (error) {
        return <div className="p-4 text-red-600">{error}</div>;
    }

    return (
        <div className="flex min-h-screen bg-gray-100">
            <Sidebar
                selectedStock={selectedStock}
                setSelectedStock={setSelectedStock}
                years={years}
                setYears={setYears}
                confidenceInterval={confidenceInterval}
                setConfidenceInterval={setConfidenceInterval}
                timeframe={timeframe}
                setTimeframe={setTimeframe}
            />
            <main className="flex-1 p-6">
                <StockSearch onSelectStock={setSelectedStock} />
                
                {loading ? (
                    <LoadingSpinner />
                ) : (
                    <>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                            <SectorOverview sectorData={sectorData} />
                            <TopPerformers data={topPerformers} timeframe={timeframe} />
                        </div>
                        
                        {stockData && (
                            <>
                                <CompanyInfo info={stockData.info} />
                                <div className="mt-6">
                                    <TechnicalChart data={stockData.data} />
                                </div>
                                {forecastData && (
                                    <>
                                        <div className="mt-6">
                                            <ForecastChart
                                                historicalData={stockData.data}
                                                forecastData={forecastData.forecast}
                                            />
                                        </div>
                                        <div className="mt-6">
                                            <ModelMetrics data={forecastData.forecast} />
                                        </div>
                                    </>
                                )}
                            </>
                        )}
                    </>
                )}
            </main>
        </div>
    );
};

export default App;