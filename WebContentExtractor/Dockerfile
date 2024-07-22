FROM node:lts

WORKDIR /usr/src/app

COPY package.json .
COPY package-lock.json .
COPY index.js .

RUN npm install

CMD ["node", "index.js"]