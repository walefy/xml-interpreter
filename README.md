# Projeto XML INTERPRETER

## Intro

Este é um projeto para analisar e armazenar informações de notas fiscais. O projeto ainda está em beta então não é recomendado o uso em casos reais!

## Features atuais

- [x] Identificação de notas faltantes
- [x] Manter registro de empresas
- [x] Verificação de cnpj nas notas
- [x] Verificação de notas duplicadas
- [x] Aceita várias notas no formato zip

## Tecnologias utilizadas

1. [MongoDB](https://www.mongodb.com/pt-br) Para o banco de dados não relacional
2. [FastAPI](https://fastapi.tiangolo.com/pt/) Para criação da api
3. [xmltodict](https://github.com/martinblech/xmltodict) Para fazer a conversão de xml para dicionário do python.
4. [beanie](https://beanie-odm.dev/) Para mapear os objetos do banco (ODM)
5. [pytest](https://docs.pytest.org/en/7.4.x/) para escrever e rodar os testes da aplicação

## Como rodar

Primeiro verifique se tem o [docker](https://www.docker.com/get-started/) e o [docker-compose](https://docs.docker.com/compose/install/) instalado.

Agora renomeie o arquivo ```.env.example``` para ```.env```

Com as duas ferramentas instaladas basta digitar o seguinte comando na raiz do projeto:

```bash
docker-compose up --build
```

Após esse comando a api vai subir no ```localhost``` utilizando a porta ```8000```.

Você pode testar se a api está funcionando acessando o endpoint ```http://localhost:8000/docs```.
