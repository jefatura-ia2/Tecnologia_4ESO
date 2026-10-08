# Se construye desde la raíz del proyecto: docker compose (context: .)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY scripts ./scripts
COPY backend/app/content ./backend/app/content
COPY backend/app/sandbox/harness.py ./backend/app/sandbox/harness.py
COPY frontend ./frontend
RUN npm run build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
