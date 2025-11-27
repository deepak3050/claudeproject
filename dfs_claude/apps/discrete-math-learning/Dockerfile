# Use nginx alpine for lightweight container
FROM nginx:alpine

# Copy the HTML/CSS/JS files to nginx html directory
COPY src/ /usr/share/nginx/html/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
