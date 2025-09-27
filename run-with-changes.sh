#!/bin/bash
docker-compose down
git pull origin main
docker-compose build --no-cache  # ✅ Force full rebuild
docker-compose up -d
