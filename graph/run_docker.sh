docker build -t graph .
docker run --rm -v "$(pwd):/data" graph
