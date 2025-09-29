FROM nginx:alpine

# Copy static site
COPY . /usr/share/nginx/html

# Basic security headers (optional)
RUN printf 'server { \n\
  listen       80; \n\
  server_name  _; \n\
  add_header X-Content-Type-Options "nosniff"; \n\
  add_header X-Frame-Options "SAMEORIGIN"; \n\
  add_header X-XSS-Protection "1; mode=block"; \n\
  root /usr/share/nginx/html; \n\
  index index.html; \n\
  location / { try_files $uri $uri/ /index.html; } \n\
} \n' > /etc/nginx/conf.d/default.conf