FROM node:18

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --chown=root:root package.json package-lock.json .
RUN ["npm", "ci"]

COPY --chown=root:root . .
CMD ["node", "./src"]

# `tini` being at `/app/sbin/tini` is pretty effing gross, but whatever
ENTRYPOINT ["/app/sbin/tini", "--"]
