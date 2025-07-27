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

  // Get proper content URL - support both dev and Docker modes
  const getContentUrl = () => {
    // If we're on project-title.localhost (Docker), use relative path via Traefik
    if (
      typeof window !== 'undefined' &&
      window.location.hostname === 'project-title.localhost'
    ) {
      return '/Plone'; // Relative path - Traefik will route to backend
    }
    // Otherwise use localhost fallback for development
    return 'http://localhost:8080/Plone';
  };

  // Always render loading screen until component is loaded on client
  if (!isClient || !Component) {
    return <LoadingScreen />;
  }

  return (
    <Component
      contentUrl={getContentUrl()}
      title="Digital Hall Pass Manager"
    />
  );
};

export default HallPassManagerRoute;
