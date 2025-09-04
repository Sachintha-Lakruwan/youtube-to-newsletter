FROM node:21 

WORKDIR /app 

COPY . . 

RUN npm install 

RUN npm run build 

RUN npm install -g serve 

EXPOSE 3000 

CMD ["serve", "dist"]

# # Stage 1: Build
# FROM node:21-alpine AS build

# WORKDIR /app
# COPY package*.json ./
# RUN npm install

# COPY . .
# RUN npm run build

# # Stage 2: Serve
# FROM nginx:alpine

# COPY --from=build /app/dist /usr/share/nginx/html

# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
