# ---------- Build stage ----------
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /app

# 1️ Copy only pubspec files first (cache dependencies)
COPY photex/pubspec.yaml photex/pubspec.lock ./photex/

WORKDIR /app/photex
RUN flutter pub get

# 2️ Copy the rest of the source
COPY photex/ ./

# 3️ Build Flutter web
RUN flutter build web --release

# ---------- Runtime stage ----------
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/photex/build/web /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
