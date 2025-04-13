FROM python:3.10  

RUN addgroup --system mercari && adduser --system trainee --ingroup mercari

USER trainee

WORKDIR /app

COPY . .

CMD ["python", "--version"]
