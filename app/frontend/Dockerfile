FROM node:10.15.3
ENV NODE_ENV development
WORKDIR ./app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
EXPOSE 8080
CMD [ "node", "server.js" ]
