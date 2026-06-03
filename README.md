# CRACKLAB

Plataforma prática de engenharia reversa de binários ELF (Linux 64-bits).

O site oficial da plataforma está disponível no arquivo `index.html`.

## Estrutura do Projeto

- `/crackmes`: Desafios práticos de engenharia reversa. Cada pasta possui o código-fonte do desafio e um `README.md` detalhado contendo a história e as instruções (writeups).
- `/docs`: Documentação de desenvolvimento, roadmap e planejamento.
- `/assets`: Assets e recursos utilizados pelo site.
- `index.html`: Landing page da plataforma (Front-end).

## Como usar os crackmes

Você pode navegar até o diretório do desafio desejado, como o de "Patch de Retorno", utilizando:

```bash
cd crackmes/02-patch-retorno
make
./challenge
```
Siga as instruções de cada `README.md` local para prosseguir.