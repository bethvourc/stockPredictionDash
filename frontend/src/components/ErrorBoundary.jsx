import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-4 bg-red-50 border border-red-400 rounded">
                    <h2 className="text-red-800 text-xl font-bold">Something went wrong</h2>
                    <button
                        onClick={() => this.setState({ hasError: false })}
                        className="mt-2 bg-red-100 text-red-800 px-4 py-2 rounded"
                    >
                        Try again
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;