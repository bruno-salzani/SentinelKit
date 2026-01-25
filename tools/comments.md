Além do clássico ' OR '1'='1 que você mostrou na imagem, existem variações mais agressivas que os invasores usam dependendo do objetivo deles (roubar dados, apagar o banco ou descobrir a estrutura do sistema).

Aqui estão os tipos mais comuns de inputs maliciosos:

1. Bypass de Administração (O "Salto")
Se o invasor sabe que o usuário administrador se chama "admin", ele pode tentar:

Input: admin' --

O que faz: O -- (ou # em alguns bancos) é o comando de comentário. Isso faz com que o banco de dados leia o nome "admin" e ignore todo o resto da linha (incluindo a verificação da senha).

2. UNION-Based SQLi (Roubo de Dados)
Este é usado para extrair dados de outras tabelas que não deveriam estar visíveis naquela página.

Input: ' UNION SELECT username, password FROM usuarios --

O que faz: Ele força o banco de dados a juntar o resultado da busca legítima com a lista completa de nomes e senhas de todos os usuários do sistema.

3. Blind SQLi (Injeção "Cega")
Quando o sistema não mostra erros na tela (como o erro em vermelho da sua imagem), o invasor faz perguntas de "Sim ou Não" para o banco de dados usando o tempo de resposta.

Input: ' OR IF(1=1, SLEEP(10), 0) --

O que faz: Se o sistema demorar 10 segundos para responder, o invasor sabe que a condição foi aceita. Ele vai testando letra por letra de cada senha assim.

4. Out-of-Band e Destrutivos
Esses são os mais perigosos para a integridade do servidor.

Input: ; DROP TABLE usuarios; --

O que faz: Tenta simplesmente deletar a tabela inteira de usuários.

Input: ; EXEC xp_cmdshell 'format c:'; --

O que faz: Em sistemas mal configurados (especialmente SQL Server antigo), pode tentar executar comandos diretamente no sistema operacional do servidor.