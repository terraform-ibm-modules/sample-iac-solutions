FROM node:18-alpine

ENV APPLICATION_HOME_DOCKER=/usr/src/app \
    APPLICATION_PORT=8080

WORKDIR $APPLICATION_HOME_DOCKER

COPY . .

RUN npm install && \
    npm run build && \
    addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs $APPLICATION_HOME_DOCKER

USER nodejs

EXPOSE $APPLICATION_PORT

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:${APPLICATION_PORT}/', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["npm","run", "start"]
