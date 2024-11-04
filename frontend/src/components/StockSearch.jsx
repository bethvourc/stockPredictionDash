import React, { useState } from 'react';
import { searchStocks } from '../services/api';

const StockSearch = ({ onSelectStock }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        const value = e.target.value;
        setQuery(value);
        
        if (value.length >= 2) {
            setLoading(true);
            try {
                const data = await searchStocks(value);
                setResults(data.results);
            } catch (error) {
                console.error('Search error:', error);
                setResults([]);
            }
            setLoading(false);
        } else {
            setResults([]);
        }
    };

    return (
        <div className="relative mb-6">
            <input
                type="text"
                value={query}
                onChange={handleSearch}
                placeholder="Search stocks..."
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            
            {loading && (
                <div className="absolute right-2 top-2">
                    <LoadingSpinner size="small" />
                </div>
            )}
            
            {results.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    {results.map((stock) => (
                        <div
                            key={stock.symbol}
                            onClick={() => {
                                onSelectStock(stock.symbol);
                                setQuery('');
                                setResults([]);
                            }}
                            className="p-2 hover:bg-gray-100 cursor-pointer"
                        >
                            <div className="font-bold">{stock.symbol}</div>
                            <div className="text-sm text-gray-600">{stock.name}</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default StockSearch;