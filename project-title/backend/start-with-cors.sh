#!/bin/bash

# CORS Fix Script for Plone Backend
echo "🚀 Starting Plone with CORS enabled for http://localhost:3000"

# Export ALL CORS environment variables
export PLONE_CORS_ALLOW_ORIGIN='http://localhost:3000'
export PLONE_CORS_ALLOW_METHODS='DELETE,GET,OPTIONS,PATCH,POST,PUT'
export PLONE_CORS_ALLOW_CREDENTIALS='true'
export PLONE_CORS_ALLOW_HEADERS='Accept,Authorization,Content-Type,X-Requested-With'
export PLONE_CORS_EXPOSE_HEADERS='Content-Length,X-JSON-Schema'
export PLONE_CORS_MAX_AGE='3600'

# Also set the old-style environment variables just in case
export CORS_ALLOW_ORIGIN='http://localhost:3000'
export CORS_ALLOW_METHODS='DELETE,GET,OPTIONS,PATCH,POST,PUT'
export CORS_ALLOW_CREDENTIALS='true'

echo "✅ CORS environment variables set"
echo "🔧 Starting Plone backend..."

# Start the backend using the instance script directly
./bin/runwsgi instance/etc/zope.ini -v 