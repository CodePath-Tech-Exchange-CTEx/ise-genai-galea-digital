#!/usr/bin/env bash

# Local development setup -- run this once before using this script:
#
#   gcloud iam service-accounts keys create ~/sa-key.json \
#     --iam-account=357619712736-compute@developer.gserviceaccount.com
#
# This generates a service account key that Docker uses for Google auth.
# The key lives at ~/sa-key.json (outside the repo, never commit it).

docker build -t streamlit-app .
docker run -p 8080:8080 \
  -v "$HOME/sa-key.json:/app/sa-key.json" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/sa-key.json \
  -e GOOGLE_CLOUD_PROJECT=amier-davis-hu \
  streamlit-app
