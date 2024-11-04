export const calculateMetrics = (data) => {
    // Calculate various performance metrics
    const y_true = data.slice(0, -365).map(d => d.y);
    const y_pred = data.slice(0, -365).map(d => d.yhat);

    const mape = calculateMAPE(y_true, y_pred);
    const rmse = calculateRMSE(y_true, y_pred);
    const r2 = calculateR2(y_true, y_pred);

    return { mape, rmse, r2 };
};

const calculateMAPE = (actual, predicted) => {
    const n = actual.length;
    return (100 / n) * actual.reduce((sum, val, i) => {
        return sum + Math.abs((val - predicted[i]) / val);
    }, 0);
};

const calculateRMSE = (actual, predicted) => {
    const n = actual.length;
    return Math.sqrt(
        actual.reduce((sum, val, i) => {
            return sum + Math.pow(val - predicted[i], 2);
        }, 0) / n
    );
};

const calculateR2 = (actual, predicted) => {
    const mean = actual.reduce((sum, val) => sum + val, 0) / actual.length;
    const ssTotal = actual.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0);
    const ssResidual = actual.reduce((sum, val, i) => {
        return sum + Math.pow(val - predicted[i], 2);
    }, 0);
    return 1 - (ssResidual / ssTotal);
};
