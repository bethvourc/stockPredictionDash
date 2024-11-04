import React from 'react';

const CompanyInfo = ({ info }) => {
    return (
        <div className="grid grid-cols-2 gap-4 p-4 bg-white rounded-lg shadow">
            <div>
                <h2 className="text-xl font-bold mb-4">Company Information</h2>
                <p className="text-lg font-semibold">{info.longName}</p>
                <p>Sector: {info.sector}</p>
                <p>Industry: {info.industry}</p>
            </div>
            <div>
                <h2 className="text-xl font-bold mb-4">Key Statistics</h2>
                <p>Market Cap: ${(info.marketCap || 0).toLocaleString()}</p>
                <p>P/E Ratio: {info.trailingPE || 'N/A'}</p>
                <p>52 Week Range: ${info.fiftyTwoWeekLow?.toFixed(2)} - ${info.fiftyTwoWeekHigh?.toFixed(2)}</p>
            </div>
        </div>
    );
};

export default CompanyInfo;