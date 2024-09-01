# Backend Service
FROM node:14 AS backend
WORKDIR /app
COPY backend/package*.json ./
RUN npm install
COPY backend/ .
EXPOSE 5000
CMD ["node", "app.js"]

# Frontend Service
FROM node:14 AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Nginx
FROM nginx:alpine
COPY deployment/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
