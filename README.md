# Respostas do FAQ Comissões W1 (antigo Assistente de Comissões)

Este repositório publica as respostas do balão de dúvidas (extensão do navegador) usado pelos consultores.
**O único arquivo que você precisa editar é o `respostas.yaml`.**

## Configurar (uma vez só)

1. No GitHub, clique em **New repository**. Nome: `w1-assistente-comissoes`, visibilidade **Public** (a publicação gratuita exige isso). Clique em **Create repository**.
2. Na página do repositório vazio, clique em **uploading an existing file**. Arraste o `respostas.yaml`, o `README.md` e a pasta `scripts` e clique em **Commit changes**.
3. Crie o arquivo da publicação automática. Clique em **Add file › Create new file** e digite o nome exatamente assim: `.github/workflows/publicar.yml`. Cole o conteúdo do arquivo `publicar.yml` que veio neste pacote e clique em **Commit changes**.
   (O GitHub não aceita pastas que começam com ponto quando você arrasta pelo Mac; por isso esse arquivo é criado à mão.)
4. Vá em **Settings › Pages**. Em *Build and deployment › Source*, escolha **GitHub Actions**.
5. Vá na aba **Actions**, clique em **Publicar respostas do balão › Run workflow**. Em cerca de 1 minuto deve aparecer um ✅ verde.
6. Confira se abre: `https://comissoes.github.io/w1-assistente-comissoes/kb.json` .

## Atualizar uma resposta (o dia a dia)

1. Abra o `respostas.yaml` no GitHub e clique no lápis (**Edit**).
2. Altere o texto. Mantenha a indentação, ou seja, os espaços no começo das linhas.
3. Clique em **Commit changes**.
4. Em cerca de 1 minuto a aba **Actions** mostra:
   - ✅ **verde:** publicado. Os consultores recebem na próxima vez que abrirem o balão (se a última checagem tiver mais de 30 minutos) ou em até 3 horas.
   - ❌ **vermelho:** algo está errado no arquivo. Clique no item e abra *Validar e gerar kb.json*: a mensagem diz qual resposta e qual campo corrigir. **Enquanto não corrigir, os consultores continuam com a versão anterior. Nada quebra para eles.**

### Para incluir uma resposta nova

Copie um bloco inteiro, do `- id:` até o fim da `resposta`. Cole no final do arquivo e troque o `id` por um código que ainda não existe, depois ajuste os demais campos. As explicações de cada campo estão no topo do `respostas.yaml`.

### Quando lançar uma versão nova da extensão (.zip)

Isso só é necessário quando o funcionamento do balão muda, não para mudar respostas.

1. Suba o .zip novo no W1nner › Arquivos › Comissões.
2. No `respostas.yaml`, aumente `extensao › versao` (ex.: `1.1.0` → `1.2.0`).

Quem estiver com a versão antiga passa a ver um aviso amarelo no balão pedindo para baixar a nova.

## Centrais de Comissões e de Estornos

As Centrais (HTML) também ficam aqui, na pasta `centrais/`, e são publicadas automaticamente junto com as respostas:

| Arquivo no repositório | Endereço publicado |
|---|---|
| `centrais/central-comissoes.html` | https://comissoes.github.io/w1-assistente-comissoes/central-comissoes.html |
| `centrais/central-estornos.html` | https://comissoes.github.io/w1-assistente-comissoes/central-estornos.html |

- **Para atualizar uma Central**, abra a pasta `centrais`, clique em **Add file › Upload files**, envie o arquivo novo **com o mesmo nome** e clique em **Commit changes**. O GitHub guarda o histórico de todas as versões (botão **History**).
- **Use nomes sem espaço e sem acento.** Se o arquivo vier com outro nome, renomeie antes de enviar, senão o endereço muda.
- O cabeçalho que falta nos arquivos exportados (`<!DOCTYPE>`, `<head>`) é completado na publicação. Não precisa mexer no arquivo.
- Arquivos com **"admin"** no nome **nunca são publicados** (ex.: a Calculadora de PPs ADMIN). Mesmo assim, não suba arquivos internos aqui: o repositório é público.
- Lembrete: o `respostas.yaml` (balão) e as Centrais são arquivos separados. Quando uma regra mudar, atualize os dois.

## Segurança

- O repositório é público: qualquer pessoa com o endereço consegue ler as respostas. Coloque aqui **somente** conteúdo que já é para consultores. Nada de dados de clientes, valores individuais, assuntos do Jurídico, CaaS ou S1NC.
- Não há senha nem chave de acesso em lugar nenhum. A extensão só **lê** este arquivo.
- A publicação bloqueia HTML perigoso (scripts, `onclick` e afins). A extensão também limpa o HTML antes de mostrar. Mesmo que alguém altere o arquivo indevidamente, não consegue rodar código no navegador dos consultores.
- Os buscadores são orientados a não indexar o endereço (`robots.txt`).
- Ative a verificação em duas etapas da sua conta do GitHub (*Settings › Password and authentication*). É a principal proteção contra alguém editar as respostas.
