from openpyxl import Workbook
import smtplib

def cria_excel_tipo(tipo, data_inicio, data_fim, avaliacoes):
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Relatorio"

    headers = ['data', 'turno', 'satisfação', 'comentário']

    for col_numero, header in enumerate(headers, start=1):
        sheet.cell(row=1, column=col_numero, value=header)
    
    quantidade_avaliacoes = len(avaliacoes)

    for nmr, linha_numero in enumerate(range(2, quantidade_avaliacoes + 2), start=2):
        data = avaliacoes[nmr - 2][0]
        satisfacao = get_emogi(avaliacoes[nmr - 2][1])
        comentarios = avaliacoes[nmr - 2][2]
        turno = avaliacoes[nmr - 2][3]

        sheet.cell(row=linha_numero, column=1, value=data)
        sheet.cell(row=linha_numero, column=2, value=turno)        
        sheet.cell(row=linha_numero, column=3, value=satisfacao)
        sheet.cell(row=linha_numero, column=4, value=comentarios)

    if data_inicio and data_fim:
        nome_arquivo = f"Relatorio {tipo}, {data_inicio} - {data_fim}.xlsx"
    else:
        nome_arquivo = f"Relatorio {tipo}.xlsx"
    
    workbook.save(nome_arquivo + ".xlsx")

def get_emogi(satisfacao):
    emojis = { '0': '😡', '1': '😟', '2': '😐', '3': '🙂', '4': '😀' }
    return emojis[satisfacao]