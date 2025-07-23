# syntax=docker/dockerfile:1
FROM varnish:7.6

LABEL maintainer="Plone Foundation <collective@plone.org>" \
      org.label-schema.name="project-title-varnish" \
      org.label-schema.description="Project Title Varnish image." \
      org.label-schema.vendor="Plone Foundation"

COPY etc/varnish.vcl /etc/varnish/default.vcl
