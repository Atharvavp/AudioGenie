docker container rm -f audiogenie_local && \
docker run -itd -v ./:/local --gpus all --name audiogenie_local audiogenie:dev && \
docker exec -it audiogenie_local bash