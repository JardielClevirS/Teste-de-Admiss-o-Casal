#Sobre o Projeto:
  - Este projeto serve para misturar uma imagem e depois montar ela de volta. Ele pega sua foto, corta em pedacinhos, coloca umas bordinhas, embaralha tudo e transforma em uma nova imagem


#O que você precisará para rodar o programa ?

 - Ter o Python instalado.
 - Instalar a biblioteca Pillow

#Para que serve a Pillow ?
 - Ela permite manipular imagens, e vamos trabalhar com isso.

#Como fazemos para instalar a Pillow ?
  - Simples, basta ir no terminal e digitar: pip install Pillow.
  Assim, a biblioteca será instalada.

#Como posso enviar minha imagem ?
 - Simples, para colocar a imagem dentro do mesmo diretorio/pasta do código.
 - O nome que o código espera é imagemEntrada.png, se a imagem estiver com outro nome, precisará renomear para "imagemEntrada.png"

#Como o código funciona ?

  -Bom, ele lê a imagem que você colocou na pasta
  
  -Divide a mesma em pedaços, o tamanho dos pedaços está configurado no código para 250x450 pixels por padrão, após isso, ele agrupa e embaralha-os.

  -Cria-se a chave, um arquivo ".txt" com todas as informações, quantos ladrilhos possui, qual era o tamanho e etc, além disso, a chave é seu mapa do tesouro para desfazer a bagunça

#Como faço para rodar o código ?

 -Coloque sua imagem(imagemEntrada.png) na mesma pasta do main.py.
 
 -Abra o terminal na pasta do Projeto.

 -Digite python main.py e aperte Enter.

 -Logo após isso, O código vai criar os arquivos imagemProcessada.png, chaveEmbaralhada.txt e imagemRestaurada.png na mesma pasta. Se der algum erro ou aviso, ele vai escrever no terminal e também no arquivo log_processamento_imagem.log.

