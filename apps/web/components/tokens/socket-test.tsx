'use client';

import React, { useState, useEffect, useCallback } from 'react';
import io from 'socket.io-client';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [pings, setPings] = useState([]);
  const [stats, setStats] = useState({
    totalPings: 0,
    avgLatency: 0,
    lastPingTime: null,
  });

  // Connect to Socket.IO server
  useEffect(() => {
    console.log('Attempting to connect to Socket.IO server...');

    const newSocket = io('http://localhost:8000', {
      transports: ['polling', 'websocket'], // Start with polling first
      upgrade: true,
      timeout: 20000,
      forceNew: true,
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    newSocket.on('connect', () => {
      console.log('Successfully connected to server');
      setIsConnected(true);
    });

    newSocket.on('disconnect', reason => {
      console.log('Disconnected from server:', reason);
      setIsConnected(false);
    });

    newSocket.on('connect_error', error => {
      console.error('Connection error:', error);
      setIsConnected(false);
    });

    newSocket.on('reconnect', attemptNumber => {
      console.log('Reconnected after', attemptNumber, 'attempts');
      setIsConnected(true);
    });

    newSocket.on('ping', data => {
      const receiveTime = new Date();
      const sentTime = new Date(data.timestamp);
      const latency = receiveTime - sentTime;

      const pingInfo = {
        id: Date.now(),
        serverTime: data.timestamp,
        receiveTime: receiveTime.toISOString(),
        latency,
        message: data.message,
      };

      setPings(prev => {
        const newPings = [pingInfo, ...prev.slice(0, 9)]; // Keep last 10 pings
        return newPings;
      });

      setStats(prev => {
        const newTotal = prev.totalPings + 1;
        const newAvgLatency =
          prev.avgLatency === 0
            ? latency
            : (prev.avgLatency * prev.totalPings + latency) / newTotal;

        return {
          totalPings: newTotal,
          avgLatency: Math.round(newAvgLatency),
          lastPingTime: receiveTime.toISOString(),
        };
      });

      // Send pong back to server (optional)
      newSocket.emit('ping_response', {
        message: 'pong',
        originalTimestamp: data.timestamp,
        responseTime: receiveTime.toISOString(),
      });
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const clearPings = useCallback(() => {
    setPings([]);
    setStats({
      totalPings: 0,
      avgLatency: 0,
      lastPingTime: null,
    });
  }, []);

  const formatTime = timestamp => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">FastAPI Socket.IO Client</h1>

        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-700">Connection Status</h2>
            <div
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}
            >
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.totalPings}</div>
              <div className="text-sm text-gray-600">Total Pings</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.avgLatency}ms</div>
              <div className="text-sm text-gray-600">Avg Latency</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm font-mono text-purple-600">
                {stats.lastPingTime ? formatTime(stats.lastPingTime) : 'None'}
              </div>
              <div className="text-sm text-gray-600">Last Ping</div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <button
            onClick={clearPings}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear Pings
          </button>
        </div>

        {/* Ping Log */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Recent Pings</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {pings.length === 0 ? (
              <div className="text-gray-500 text-center py-8">Waiting for pings from server...</div>
            ) : (
              pings.map(ping => (
                <div key={ping.id} className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-medium text-gray-700">{ping.message}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        Received: {formatTime(ping.receiveTime)}
                      </span>
                    </div>
                    <div className="text-right">
                      <div
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          ping.latency < 50
                            ? 'bg-green-100 text-green-800'
                            : ping.latency < 100
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {ping.latency}ms
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
