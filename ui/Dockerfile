FROM node:18.20-alpine as build
WORKDIR /app
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install
COPY . .
RUN NODE_OPTIONS="--max-old-space-size=4096" pnpm run build

FROM node:18.20-alpine as stage
WORKDIR /app
COPY --from=build /app/dist /app/dist
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3333"]
