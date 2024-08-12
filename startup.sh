#!/bin/bash
exec uvicorn src.main:app --host 0.0.0.0 --port 9999 --forwarded-allow-ips='*' --proxy-headers