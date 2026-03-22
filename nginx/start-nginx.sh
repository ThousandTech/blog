#!/bin/sh
set -eu

CERT_DIR="/etc/letsencrypt/live/thousand-tech.com"
HTTP_TEMPLATE="/etc/nginx/templates/default-http.conf"
HTTPS_TEMPLATE="/etc/nginx/templates/default-https.conf"
TARGET_CONF="/etc/nginx/conf.d/default.conf"

if [ -f "$CERT_DIR/fullchain.pem" ] && [ -f "$CERT_DIR/privkey.pem" ]; then
  cp "$HTTPS_TEMPLATE" "$TARGET_CONF"
else
  cp "$HTTP_TEMPLATE" "$TARGET_CONF"
fi

exec nginx -g "daemon off;"

