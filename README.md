# nlth2
Source for the NLTH2 cafe app (cafe.alsionschool.org)

The various old versions are at bitbucket.org/tahabi/nlth-cafe/.

This new-ish version is now reasonably Dockerized.

The app requires you to mount the location of the database and
a socket; alternatively you can change the command to have
gunicorn bind to a port/address and add a port mapping to
`docker run`. I run this behind nginx with it binding to a socket.

To create the container run

    docker build -t <tag> .
    docker run --name nlth2-alpine -v ~<dir>/nlth2x.db:/app/nlth2x.db -v ~<dir>/socket:/app/socket <tag>

I could probably do a lot of things in this app better. Fun project,
useful for Alsion as well as for learning how to use Docker.