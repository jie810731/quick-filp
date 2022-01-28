## how to build

docker build -t quickflip .

## how to run

docker run -i -t --rm -v "$PWD":/usr/src/myapp -w /usr/src/myapp
--name {{container_name}} quickflip
