FROM nginx

COPY default.conf /etc/nginx/conf.d/default.conf
COPY fullchain.pem /etc/letsencrypt/live/spiderwebquizzes.me/fullchain.pem
COPY privkey.pem /etc/letsencrypt/live/spiderwebquizzes.me/privkey.pem
COPY options-ssl-nginx.conf /etc/letsencrypt/options-ssl-nginx.conf
COPY ssl-dhparams.pem /etc/letsencrypt/ssl-dhparams.pem
#TODO
#COPY cert.pem /root/cert.pem
#COPY private.key /root/private.key