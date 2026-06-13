FROM node:18.20-alpine as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build

FROM node:18.20-alpine as stage
WORKDIR /app
COPY --from=build /app/dist /app/dist
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3333"]
