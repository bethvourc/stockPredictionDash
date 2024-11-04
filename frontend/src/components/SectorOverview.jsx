import React from 'react';
import { Treemap } from 'recharts';

const SectorOverview = ({ sectorData }) => {
    const data = {
        name: 'S&P 500',
        children: Object.entries(sectorData).map(([sector, data]) => ({
            name: sector,
            size: data.count,
            value: data.performance.daily
        }))
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Sector Overview</h2>
            <div style={{ width: '100%', height: '400px' }}>
                <Treemap
                    data={[data]}
                    dataKey="value"
                    aspectRatio={4/3}
                    stroke="#fff"
                    fill="#8884d8"
                >
                    <Tooltip content={<CustomTooltip />} />
                </Treemap>
            </div>
        </div>
    );
};

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="bg-white p-2 shadow rounded">
                <p className="font-bold">{data.name}</p>
                <p>Companies: {data.size}</p>
                <p>Performance: {data.value.toFixed(2)}%</p>
            </div>
        );
    }
    return null;
};

export default SectorOverview;