# ---------- Build stage ----------
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /app

# Copy Flutter project
COPY photex/ ./photex/

WORKDIR /app/photex

# Enable web support
RUN flutter config --enable-web

# Install dependencies
RUN flutter pub get

# Build Flutter web app
RUN flutter build web --release

# ---------- Runtime stage ----------
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy Flutter build output
COPY --from=builder /app/photex/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
