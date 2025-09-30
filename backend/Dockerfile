FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY backend/package*.json ./
RUN npm install --omit=dev
COPY backend/ ./
EXPOSE 8080
CMD ["node", "server.js"]