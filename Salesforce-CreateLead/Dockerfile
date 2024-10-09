FROM node:20.18.0-alpine AS build

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm ci --only=production

FROM node:20.18.0-alpine

WORKDIR /usr/src/app

COPY --from=build /usr/src/app/node_modules ./node_modules

COPY . .

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

CMD [ "node", "index.js" ]