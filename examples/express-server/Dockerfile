FROM node:alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run dev

EXPOSE 9999
CMD ["npm", "start"]
