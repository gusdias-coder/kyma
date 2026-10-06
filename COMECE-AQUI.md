# Colocar a KYMA no GitHub Pages

Esta versão foi feita para funcionar no GitHub Pages, com o visual e as interações do projeto KYMA. É uma apresentação de conceito: a sacola funciona no navegador e o checkout simula a experiência. Não há venda, cobrança, estoque real ou envio de pedidos.

## 1. Extrair o pacote

1. Baixe `KYMA-GitHub-Pages.zip`.
2. Clique com o botão direito no arquivo e escolha **Extrair Tudo**.
3. Abra a pasta extraída. Você deve encontrar `index.html`, `assets`, `.github`, `package.json` e este guia no mesmo nível.
4. Não envie o ZIP inteiro para o repositório. Envie os arquivos extraídos.

## 2. Criar o repositório

1. Entre na sua conta do GitHub.
2. Clique no **+**, no alto da página, e em **New repository**.
3. No nome, use `kyma-site` ou outro nome que preferir.
4. Marque **Public** para usar o GitHub Pages no plano gratuito.
5. Marque a opção para criar um README e clique em **Create repository**.

Se você já tem um repositório para essa nova versão, use-o. Antes de substituir arquivos existentes, baixe uma cópia em **Code → Download ZIP**.

## 3. Enviar os arquivos

1. No repositório, clique em **Add file → Upload files**.
2. Abra a pasta extraída no Explorador do Windows.
3. Selecione o conteúdo da pasta, incluindo `assets`, `scripts`, `docs` e `.github`, e arraste para a área de envio do GitHub.
4. Confira que `index.html` aparece diretamente na raiz. O caminho não deve ser `kyma-github-pages/index.html`.
5. Confira também que existe `.github/workflows/pages.yml` na lista.
6. Na mensagem de alteração, escreva `Add KYMA GitHub Pages presentation`.
7. Salve em **Commit changes** na branch `main`.

Se a pasta `.github` não entrar pelo arraste, use **Add file → Create new file**, digite `.github/workflows/pages.yml` como nome e copie o conteúdo do arquivo de mesmo nome incluído no pacote. Salve na `main`.

## 4. Ativar a publicação

1. Abra **Settings** do repositório.
2. No menu lateral, clique em **Pages**.
3. Em **Build and deployment → Source**, selecione **GitHub Actions**.
4. Abra a aba **Actions**.
5. Escolha **Check and publish KYMA presentation**.
6. Clique em **Run workflow**, mantenha `main` e confirme em **Run workflow**. Esse passo é útil se o primeiro envio ocorreu antes de ativar o Pages.
7. Aguarde os dois trabalhos, `check` e `deploy`, ficarem verdes.
8. Volte a **Settings → Pages** e clique em **Visit site**.

O endereço será informado pelo GitHub. Para um repositório chamado `kyma-site`, normalmente termina em `/kyma-site/`. Não é necessário configurar banco de dados, chaves de pagamento ou senha de serviço.

## 5. Testar o site publicado

1. Abra a página inicial no celular e no computador.
2. Abra **Buscar**, digite `moletom` e confira as quatro referências.
3. Explore categorias, coleções e filtros.
4. Abra uma peça, selecione o tamanho e adicione à sacola.
5. Teste os favoritos, a quantidade e o cupom ilustrativo `KYMA10`.
6. Abra **Simular checkout**, escolha o estado e conclua. A página informa que nenhum pedido ou pagamento foi criado.
7. Atualize a página para verificar a persistência da sacola nesse navegador.

## Atualizar depois

Edite os arquivos no GitHub e salve na `main`. A configuração incluída verifica e publica cada alteração nessa branch. Alterações propostas em pull requests são verificadas, mas não ganham um segundo site de prévia automaticamente.

Os produtos e textos ficam em `assets/js/data.js`; o visual fica em `assets/css/styles.css`; a marca pode ser substituída em `assets/brand/kyma-logo.svg`. As fotos atuais são referências, com créditos em `docs/MEDIA-CREDITS.md`.

## Se aparecer um erro

| Situação | Como resolver |
| --- | --- |
| Não há execução em Actions | Confira `.github/workflows/pages.yml` e a branch `main`. |
| Erro ao configurar Pages | Selecione **GitHub Actions** em **Settings → Pages** e execute novamente. |
| Publicação recusada pelo ambiente | Em **Settings → Environments → github-pages**, confira que `main` pode publicar. |
| Página 404 ou sem estilos | Confira que `index.html` e `assets` estão na raiz, com os nomes e letras originais. |
| Site antigo após atualizar | Aguarde a execução ficar verde e recarregue com `Ctrl + F5`. |
| Pasta `.github` difícil de enviar | Crie o arquivo pelo caminho completo, conforme a etapa 3. |

Como alternativa, o site também pode ser servido por **Settings → Pages → Deploy from a branch → main → /(root)**. Nesse modo a publicação usa diretamente os arquivos da raiz e não depende do workflow incluído para publicar. Use apenas um dos modos de publicação.

## O que esta versão permite

Apresentar e testar a identidade, o catálogo e a experiência da KYMA. Para vender de verdade, será necessário usar outra hospedagem e integrar serviços de pagamento, estoque e pedidos. O GitHub restringe o uso de Pages para lojas e transações sensíveis: [regras oficiais](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

Este pacote foi validado localmente. A confirmação da publicação na sua conta ocorre quando o GitHub mostrar os trabalhos verdes e o endereço em **Visit site**.
