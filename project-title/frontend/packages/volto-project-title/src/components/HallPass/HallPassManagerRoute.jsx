/**
 * Hall Pass Manager Route Component
 *
 * Client-only route that prevents hydration mismatches
 */

import React, { useState, useEffect } from 'react';

const LoadingScreen = () => (
  <div style={{ padding: '40px', textAlign: 'center' }}>
    <h1>Digital Hall Pass Manager</h1>
    <p>Loading...</p>
  </div>
);

const HallPassManagerRoute = () => {
  const [isClient, setIsClient] = useState(false);
  const [Component, setComponent] = useState(null);

  useEffect(() => {
    setIsClient(true);
    import('./HallPassManager').then((module) => {
      setComponent(() => module.default);
    });
  }, []);

  // Always render loading screen until component is loaded on client
  if (!isClient || !Component) {
    return <LoadingScreen />;
  }

  return (
    <Component
      contentUrl="http://localhost:8080"
      title="Digital Hall Pass Manager"
    />
  );
};

export default HallPassManagerRoute;
