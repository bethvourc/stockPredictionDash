import React from 'react';
import { SP500_TICKERS } from '../constants';

const Sidebar = ({ 
    selectedStock, 
    setSelectedStock, 
    years, 
    setYears, 
    confidenceInterval, 
    setConfidenceInterval 
}) => {
    return (
        <div className="w-64 bg-white shadow-lg p-4">
            <h2 className="text-xl font-bold mb-4">Parameters</h2>
            
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Select Stock</label>
                <select
                    value={selectedStock}
                    onChange={(e) => setSelectedStock(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {SP500_TICKERS.map(ticker => (
                        <option key={ticker} value={ticker}>{ticker}</option>
                    ))}
                </select>
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">
                    Years of Prediction: {years}
                </label>
                <input
                    type="range"
                    min="1"
                    max="4"
                    value={years}
                    onChange={(e) => setYears(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">
                    Confidence Interval: {confidenceInterval}%
                </label>
                <input
                    type="range"
                    min="80"
                    max="95"
                    value={confidenceInterval}
                    onChange={(e) => setConfidenceInterval(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
            </div>
        </div>
    );
};

export default Sidebar;
