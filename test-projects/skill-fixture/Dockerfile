# scan-container-image fixture — Intentionally vulnerable — do not deploy

# CIS-DOCKER: no specific version pinned (mutable tag)
FROM node:18

# CIS-DOCKER: running as root
USER root

WORKDIR /app

# CIS-DOCKER: ADD from remote URL — bypasses layer cache integrity
ADD https://example.invalid/tool.tar.gz /tmp/tool.tar.gz

# CIS-DOCKER: apt-get without --no-install-recommends, no version pins
RUN apt-get update && apt-get install -y curl wget netcat

COPY package.json package-lock.json ./

# CIS-DOCKER: npm install with scripts enabled (postinstall runs arbitrary code)
RUN npm install --ignore-scripts=false

COPY . .

# CIS-DOCKER: sensitive values baked into image layer
ENV DB_PASSWORD=hardcoded-db-pass
ENV API_KEY=stripe_live_fake_key_placeholder

# CIS-DOCKER: no HEALTHCHECK defined
# CIS-DOCKER: no USER instruction before CMD (still root)
# CIS-DOCKER: no read-only filesystem
# CIS-DOCKER: exposes unnecessary port
EXPOSE 3000
EXPOSE 22

CMD ["node", "src/app.js"]
