FROM node:18

RUN npm install pm2 -g

WORKDIR /app

COPY ./package.json /app/
COPY ./package-lock.json /app/

RUN npm install

COPY ./ /app/

RUN npm run build

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

EXPOSE ${NUXT_PORT}

# ENTRYPOINT ["pm2", "start", "ecosystem.config.js"]
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
