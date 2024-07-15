# fk-affiliate-avrc
This is a Famekeeda Affiliate Automated Vendor Report Creation

Publish this to the Docker

run using docker-compose

if you want to install into a new machine here are the steps

1. Firstly setup a new device and install all packages required
   - docker
   - nginx

2. import the project
   - git clone git <link>
   - git pull if changes are there

 4. run the commands
   - sudo docker-compose build
   - sudo docker-compose up (-d parameter for running in the background)
   - sudo docker-compose ps (to check if the docker container is running or not)
   - sudo docker-compose logs <container id>
   - sudo docker-compose down (to stop the container)

5. setup nignx
   - go to /etc/nginx/sites-available/
   - create a file (name it as domain name - avrc.famekeeda.com)
   - set reverse proxy for it
   - install certbot for domain bypass
   - test the config
   - restart nginx and
   - ENJOY!
