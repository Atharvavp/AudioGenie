docker container rm -f audiogenie_minimal && \
docker run -itd -p 7860:7860 --name audiogenie_minimal --gpus all dbfvoiceai/noise_cancellation:v0