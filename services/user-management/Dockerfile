FROM node:21-alpine

WORKDIR /app

COPY . . 

RUN npm install --production

EXPOSE 8080

CMD ["node", "src/app.js"]