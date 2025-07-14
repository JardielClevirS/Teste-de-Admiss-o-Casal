import os
import random
import logging
# import argparse # Removido

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps


#CONSTANTES GLOBAIS:
LARGURA_LADRILHO = 250
ALTURA_LADRILHO = 450
TAMANHO_BORDA = 20
COR_DA_BORDA = "black"

if isinstance(COR_DA_BORDA, str):
    COR_DA_BORDA = ImageColor.getrgb(COR_DA_BORDA)

# A linha abaixo vai continuar por ser uma checagem importante pra nao quebrar.
assert isinstance(COR_DA_BORDA, tuple) and len(COR_DA_BORDA) == 3 and all(isinstance(validacao, int) for validacao in COR_DA_BORDA), \
        "Cor inválida, por favor, utilize uma cor RGB."

IMAGEM_DE_ENTRADA = "imagemEntrada.png"
IMAGEM_DE_SAIDA = "imagemProcessada.png"
CHAVE_EMBARALHADA = "chaveEmbaralhada.txt"
IMAGEM_RESTAURADA = "imagemRestaurada.png"

def dividirImagens(caminhoDeImagem: str, caminhoDeSaidaImagem: str, caminhoDeChave: str):
    #Esta funçaõ irá servir para quebrar, dividir a imagem enviada.
    logger.info(f"Carregando a imagem de entrada: '{caminhoDeImagem}'")
    try:
        imagemOriginal = Image.open(caminhoDeImagem)
    except FileNotFoundError:
        logger.error(f"Erro: O arquivo da imagem '{caminhoDeImagem}' nao foi encontrado. Certifique-se de que a imagem existe no caminho especificado.")
        return
    except IOError as e:
        logger.error(f"Erro de E/S ao abrir a imagem '{caminhoDeImagem}': {e}")
        return
    except Exception as e:
        logger.error(f"Um erro inesperado ocorreu ao carregar a imagem: {e}")
        return

    #Para obter a altura e largura da imagem.
    larguraTotal, alturaTotal = imagemOriginal.size

    #Listas e Dicionário:
    grupos = {}
    listaGrupos = []
    indexGrupoPorTamanho = {}
    grupoPorPosicao = []
    indexEmbaralhadoPorPosicao = []

    #Calculo do numero total de Colunas e Linhas
    #OBS: arredonando para cima para incluir a parte que sobra
    numDeColunas = (larguraTotal + LARGURA_LADRILHO - 1) // LARGURA_LADRILHO
    numDeLinhas = (alturaTotal + ALTURA_LADRILHO - 1) // ALTURA_LADRILHO
    logger.info(f"A imagem sera dividida em {numDeLinhas} linhas e {numDeColunas} colunas.")

    #Para iterar sobre limhas e colunas:
    for i in range(numDeLinhas):
        for j in range(numDeColunas):
            areaDeCorte = (
                j * LARGURA_LADRILHO,
                i * ALTURA_LADRILHO,
                min(((j + 1) * LARGURA_LADRILHO), larguraTotal),
                min(((i + 1) * ALTURA_LADRILHO), alturaTotal)
            )
            #Recorta a imagem original:
            ladrilho = imagemOriginal.crop(areaDeCorte)
            tamanhoLadrilho = (areaDeCorte[2] - areaDeCorte[0], areaDeCorte[3] - areaDeCorte[1])
            #Armazena a posiçao dele:
            dadosDoLadrilhoOriginal = (i, j, areaDeCorte, ladrilho)

            if tamanhoLadrilho not in grupos:
                grupos[tamanhoLadrilho] = []
                indexGrupo = len(listaGrupos)
                indexGrupoPorTamanho[tamanhoLadrilho] = indexGrupo
                listaGrupos.append(tamanhoLadrilho)
            else:
                indexGrupo = indexGrupoPorTamanho[tamanhoLadrilho]

            grupos[tamanhoLadrilho].append(dadosDoLadrilhoOriginal)
            grupoPorPosicao.append(indexGrupo)

    # O sistema embaralha os ladrilhos dentro de cada grupo para a posiçao embaralhada.
    indicesEmbaralhadosPorGrupo = {}
    for tamanhoAtual, listaLadrilhosDoGrupo in grupos.items():
        numPosicoesNoGrupo = len(listaLadrilhosDoGrupo)
        indicesOriginaisDoGrupo = list(range(numPosicoesNoGrupo))
        indicesEmbaralhadosDoGrupo = indicesOriginaisDoGrupo[:]
        random.shuffle(indicesEmbaralhadosDoGrupo)
        indicesEmbaralhadosPorGrupo[tamanhoAtual] = indicesEmbaralhadosDoGrupo

    # Isso ajuda a organizar a ordem final dos ladrilhos embaralhados.
    contadoresPorGrupo = {index: 0 for index in range(len(listaGrupos))}
    for indexPosicaoOriginal, indexGrupoLadrilho in enumerate(grupoPorPosicao):
        indexLocal = contadoresPorGrupo[indexGrupoLadrilho]
        contadoresPorGrupo[indexGrupoLadrilho] += 1
        tamanhoLadrilho = listaGrupos[indexGrupoLadrilho]
        indexEmbaralhadoNoGrupo = indicesEmbaralhadosPorGrupo[tamanhoLadrilho][indexLocal]
        indexEmbaralhadoPorPosicao.append(indexEmbaralhadoNoGrupo)

    # Aquio se cria o diretorio para a saida de chave.
    diretorioChave = os.path.dirname(caminhoDeChave)
    if diretorioChave and not os.path.exists(diretorioChave):
        try:
            os.makedirs(diretorioChave)
            logger.info(f"Criando o diretório para a chave: '{diretorioChave}'")
        except OSError as erro:
            logger.error(f"Erro ao criar diretório para a chave '{diretorioChave}': {erro}")
            return

    try:
        with open(caminhoDeChave, "w") as escreve:
            escreve.write(f"{numDeLinhas},{numDeColunas},{LARGURA_LADRILHO},{ALTURA_LADRILHO},{TAMANHO_BORDA},{COR_DA_BORDA[0]},{COR_DA_BORDA[1]},{COR_DA_BORDA[2]}\n")
            escreve.write(",".join(map(str, grupoPorPosicao)) + "\n")
            escreve.write(",".join(map(str, indexEmbaralhadoPorPosicao)) + "\n")
        logger.info(f"Chave de embaralhamento salva em '{caminhoDeChave}'.")
    except IOError as erro:
        logger.error(f"Erro de E/S ao salvar a chave em '{caminhoDeChave}': {erro}")
        return

    #Preparando para montar a imagem final ja embaralhada.
    larguraColunasProcessada = [
        min(LARGURA_LADRILHO, larguraTotal - j * LARGURA_LADRILHO) for j in range(numDeColunas)
    ]
    alturaLinhasProcessada = [
        min(ALTURA_LADRILHO, alturaTotal - i * ALTURA_LADRILHO) for i in range(numDeLinhas)
    ]

    #Calculando imagem final com bordas.
    larguraFinalProcessada = sum(larguraColuna + 2 * TAMANHO_BORDA for larguraColuna in larguraColunasProcessada)
    alturaFinalProcessada = sum(alturaLinha + 2 * TAMANHO_BORDA for alturaLinha in alturaLinhasProcessada)

    # Cria uma nova imagem em branco para colar os ladrilhos embaralhados.
    imagemFinal = Image.new(imagemOriginal.mode, (larguraFinalProcessada, alturaFinalProcessada))
    logger.info("Montando a imagem final embaralhada com bordas.")

    # Itera sobre as posiçoes originais para colocar os ladrilhos embaralhados.
    for indexPosicaoOriginal, indexGrupoLadrilho in enumerate(grupoPorPosicao):
        tamanhoLadrilho = listaGrupos[indexGrupoLadrilho]
        indexEmbaralhadoNoGrupo = indexEmbaralhadoPorPosicao[indexPosicaoOriginal]

        #Aqui o o traço esta sendo usado porque quero apenas os ultimos dois valores.
        _, _, caixaOriginal, ladrilhoOriginal = grupos[tamanhoLadrilho][indexEmbaralhadoNoGrupo]

        ladrilhoComBorda = ImageOps.expand(ladrilhoOriginal, border = TAMANHO_BORDA, fill = COR_DA_BORDA)

        novaLinha = indexPosicaoOriginal // numDeColunas
        novaColuna = indexPosicaoOriginal % numDeColunas

        posicaoX = sum(larguraColuna + 2 * TAMANHO_BORDA for larguraColuna in larguraColunasProcessada[:novaColuna])
        posicaoY = sum(alturaLinha + 2 * TAMANHO_BORDA for alturaLinha in alturaLinhasProcessada[:novaLinha])

        imagemFinal.paste(ladrilhoComBorda, (posicaoX, posicaoY))

    diretorioSaidaImagem = os.path.dirname(caminhoDeSaidaImagem)
    if diretorioSaidaImagem and not os.path.exists(diretorioSaidaImagem):
        try:
            os.makedirs(diretorioSaidaImagem)
            logger.info(f"Criado diretório para a imagem processada: '{diretorioSaidaImagem}'")
        except OSError as erro:
            logger.error(f"Erro ao criar diretório para a imagem processada '{diretorioSaidaImagem}': {erro}")
            return

    imagemFinal.save(caminhoDeSaidaImagem)
    logger.info(f"Processo de embaralhamento concluido! Imagem salva em '{caminhoDeSaidaImagem}'.")

def reverterProcesso(caminhoImagemProcessada: str, caminhoChave: str, caminhoImagemRestaurada: str):
    logger.info("\n--- Iniciando processo de reversão ---")
    try:
        imagemProcessada = Image.open(caminhoImagemProcessada)
        with open(caminhoChave, "r") as f:
            # Lendo as infos da chave para saber como reverter, tipo as dimensoes e a cor da borda.
            cabecalho = list(map(int, f.readline().split(",")))
            # Pegando as posiçoes originais dos grupos e os indices embaralhados.
            grupoPorPosicao = list(map(int, f.readline().split(",")))
            indexEmbaralhadoPorPosicao = list(map(int, f.readline().split(",")))
    except FileNotFoundError:
        logger.error(f"Erro: Imagem processada ('{caminhoImagemProcessada}') ou arquivo de chave ('{caminhoChave}') nao encontrado.")
        return
    except IOError as erro:
        logger.error(f"Erro de E/S ao ler arquivo: {erro}")
        return
    except ValueError:
        logger.error(f"Erro: O arquivo de chave '{caminhoChave}' esta corrompido ou em formato invalido.")
        return
    except Exception as exception:
        logger.error(f"Um erro inesperado ocorreu ao carregar a imagem ou a chave: {exception}")
        return

    numLinhasChave, numColunasChave, larguraLadrilhoChave, alturaLadrilhoChave, \
    tamanhoBordaChave, redChave, greenChave, blueChave = cabecalho
    # Desempacota os dados do cabeçalho da chave para usar na reversao da imagem.
    corBordaChave = (redChave, greenChave, blueChave)

    if LARGURA_LADRILHO != larguraLadrilhoChave or \
       ALTURA_LADRILHO != alturaLadrilhoChave or \
       TAMANHO_BORDA != tamanhoBordaChave or \
       COR_DA_BORDA != corBordaChave:
        logger.warning("Atençao: As constantes (LADRILHO, BORDA, COR) no codigo sao diferentes das salvas na chave. Isso pode causar uma restauraçao incorreta.")

    # Calculando o tamanho do ladrilho com a borda para conseguir cortar certo.
    larguraLadrilhoComBorda = larguraLadrilhoChave + (2 * tamanhoBordaChave)
    alturaLadrilhoComBorda = alturaLadrilhoChave + (2 * tamanhoBordaChave)

    larguraTotalProcessada, alturaTotalProcessada = imagemProcessada.size

    # Ajustando as larguras e alturas das colunas e linhas para considerar a borda.
    larguraColunasProcessada = [
        min(larguraLadrilhoComBorda, larguraTotalProcessada - j * larguraLadrilhoComBorda)
        for j in range(numColunasChave)
    ]
    alturaLinhasProcessada = [
        min(alturaLadrilhoComBorda, alturaTotalProcessada - i * alturaLadrilhoComBorda)
        for i in range(numLinhasChave)
    ]

    # Armazenando os ladrilhos com borda em grupos pra organizar.
    gruposEmbaralhados = {}
    posicaoYAtual = 0

    for i in range(numLinhasChave):
        alturaLadrilhoProcessado = alturaLinhasProcessada[i]
        posicaoXAtual = 0
        for j in range(numColunasChave):
            larguraLadrilhoProcessado = larguraColunasProcessada[j]

            caixaCorteComBorda = (
                posicaoXAtual,
                posicaoYAtual,
                posicaoXAtual + larguraLadrilhoProcessado,
                posicaoYAtual + alturaLadrilhoProcessado
            )
            ladrilhoComBorda = imagemProcessada.crop(caixaCorteComBorda)

            # A funçao retira a borda de cada ladrilho pra voltar ao original.
            esquerda = tamanhoBordaChave if ladrilhoComBorda.width >= (2 * tamanhoBordaChave) else 0
            superior = tamanhoBordaChave if ladrilhoComBorda.height >= (2 * tamanhoBordaChave) else 0
            direita = ladrilhoComBorda.width - tamanhoBordaChave if ladrilhoComBorda.width >= (2 * tamanhoBordaChave) else ladrilhoComBorda.width
            inferior = ladrilhoComBorda.height - tamanhoBordaChave if ladrilhoComBorda.height >= (2 * tamanhoBordaChave) else ladrilhoComBorda.height

            ladrilhoSemBorda = ladrilhoComBorda.crop((esquerda, superior, direita, inferior))

            indexPosicaoAtualLinear = i * numColunasChave + j
            indexGrupoDoLadrilho = grupoPorPosicao[indexPosicaoAtualLinear]

            if indexGrupoDoLadrilho not in gruposEmbaralhados:
                gruposEmbaralhados[indexGrupoDoLadrilho] = []
            gruposEmbaralhados[indexGrupoDoLadrilho].append(ladrilhoSemBorda)

            posicaoXAtual += larguraLadrilhoProcessado
        posicaoYAtual += alturaLadrilhoProcessado

    # Mapeando as posiçoes para reverter o embaralhamento e colocar os ladrilhos no lugar certo.
    posicoesPorGrupo = {}
    for indexPosicaoOriginal, indexGrupoDoLadrilho in enumerate(grupoPorPosicao):
        if indexGrupoDoLadrilho not in posicoesPorGrupo:
            posicoesPorGrupo[indexGrupoDoLadrilho] = []
        posicoesPorGrupo[indexGrupoDoLadrilho].append(indexPosicaoOriginal)

    numTotalLadrilhos = len(grupoPorPosicao)
    mapaReverso = [None] * numTotalLadrilhos

    for indexGrupo, posicoesOriginaisDoGrupo in posicoesPorGrupo.items():
        for indexLocalNoGrupo, indexPosicaoOriginal in enumerate(posicoesOriginaisDoGrupo):
            idxEmbaralhadoNoGrupo = indexEmbaralhadoPorPosicao[indexPosicaoOriginal]
            idxOriginalDoLadrilhoQueEstavaAqui = posicoesOriginaisDoGrupo[idxEmbaralhadoNoGrupo]
            mapaReverso[idxOriginalDoLadrilhoQueEstavaAqui] = (indexGrupo, indexLocalNoGrupo)

    # Cria a imagem restaurada com o tamanho baseado nos ladrilhos, pode ficar um pouco maior que a original se ela era 'quebrada'.
    imagemRestaurada = Image.new(imagemProcessada.mode, (numColunasChave * LARGURA_LADRILHO, numLinhasChave * ALTURA_LADRILHO))
    logger.info("Remontando a imagem original a partir da chave.")

    # Colocando cada ladrilho sem a borda na sua posiçao original.
    for indexPosicaoOriginal, (indexGrupoDoLadrilho, indexEmbaralhadoNoGrupo) in enumerate(mapaReverso):
        ladrilhoSemBorda = gruposEmbaralhados[indexGrupoDoLadrilho][indexEmbaralhadoNoGrupo]

        linhaOriginal = indexPosicaoOriginal // numColunasChave
        colunaOriginal = indexPosicaoOriginal % numColunasChave

        posicaoXRestaurada = colunaOriginal * LARGURA_LADRILHO
        posicaoYRestaurada = linhaOriginal * ALTURA_LADRILHO

        imagemRestaurada.paste(ladrilhoSemBorda, (posicaoXRestaurada, posicaoYRestaurada))

    diretorioRestaurada = os.path.dirname(caminhoImagemRestaurada)
    if diretorioRestaurada and not os.path.exists(diretorioRestaurada):
        try:
            os.makedirs(diretorioRestaurada)
            logger.info(f"Criado diretório para a imagem restaurada: '{diretorioRestaurada}'")
        except OSError as erro:
            logger.error(f"Erro ao criar diretório para a imagem restaurada '{diretorioRestaurada}': {erro}")
            return

    imagemRestaurada.save(caminhoImagemRestaurada)
    logger.info(f"Imagem restaurada com sucesso em '{caminhoImagemRestaurada}'.")

def main():
    # Definindo as açoes e caminhos fixos para este exemplo.
    acaoEscolhida = "ambos"
    entrada = IMAGEM_DE_ENTRADA
    saida = IMAGEM_DE_SAIDA
    chave = CHAVE_EMBARALHADA
    restaurada = IMAGEM_RESTAURADA

    # Checa se a imagem de entrada existe antes de começar o trabalho.
    if acaoEscolhida in ["processar", "ambos"] and not os.path.exists(entrada):
        logger.error(f"Erro: A imagem de entrada '{entrada}' nao foi encontrada.")
        return

    if acaoEscolhida in ["processar", "ambos"]:
        logger.info(f"Iniciando processo de embaralhamento.")
        dividirImagens(
            caminhoDeImagem = entrada,
            caminhoDeSaidaImagem = saida,
            caminhoDeChave = chave
        )
        if not os.path.exists(saida):
            logger.error(f"O processo de embaralhamento falhou. A imagem de saida '{saida}' nao foi criada.")
            if acaoEscolhida == "ambos":
                return

    if acaoEscolhida in ["reverter", "ambos"]:
        if not os.path.exists(saida):
            logger.error(f"Erro: A imagem processada '{saida}' nao foi encontrada para a reversao. "
                         "Execute o 'processar' primeiro ou forneça uma imagem processada existente.")
            return
        if not os.path.exists(chave):
            logger.error(f"Erro: O arquivo de chave '{chave}' nao foi encontrado para a reversao.")
            return

        logger.info(f"Iniciando processo de reversão.")
        reverterProcesso(
            caminhoImagemProcessada = saida,
            caminhoChave = chave,
            caminhoImagemRestaurada = restaurada
        )
        if not os.path.exists(restaurada):
            logger.error(f"O processo de reversao falhou. A imagem restaurada '{restaurada}' nao foi criada.")

    logger.info("Operaçoes concluidas com sucesso.")

if __name__ == "__main__":
    main()