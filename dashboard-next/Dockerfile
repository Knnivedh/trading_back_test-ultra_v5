FROM node:18-alpine

WORKDIR /app

# Copy dashboard files
COPY dashboard-next/package*.json ./
RUN npm install

COPY dashboard-next ./

# Build Next.js
RUN npm run build

# Expose port
EXPOSE 3000

# Start Next.js
CMD ["npm", "start"]
