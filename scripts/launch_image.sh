docker container rm -f audiogenie_minimal && \
docker run -itd -p 7860:7860 --name audiogenie_minimal -v ./temp:/temp --gpus all ambatechai/noise_cancellation:v0_runtime