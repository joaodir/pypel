from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, F, Count, Subquery, OuterRef, FloatField, Sum, ExpressionWrapper
from .models import Usuario, Perfil, Departamento, Atividade
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce
from django.http import HttpResponse

#CADASTRO DE DEPARTAMENTOS
@login_required
def departamentos(request):
    if request.session.get('perfil_atual') not in {'Administrador'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_departamento":
            nome = request.POST.get('txtNome')
            
            if (nome == 'Geral'):
                messages.error(request, 'Você não pode cadastrar um departamento chamado "Geral", pois esse nome é reservado para o sistema! Use outro.')
                return redirect('cadastros:departamentos')
            
            sigla = request.POST.get('txtSigla')

            if Departamento.objects.filter(nome=nome).exists():
                messages.error(request, 'Nome de departamento já cadastrado nesta unidade!')
                return redirect('cadastros:departamentos')

            departamento = Departamento(
                nome=nome,
                sigla=sigla,
            )
            
            departamento.save()

            messages.success(request, 'Departamento cadastrado com sucesso!')
            return redirect('cadastros:departamentos')

        elif acao == "alterar_departamento":
            departamento_id = request.POST.get('txtId')
            departamento = Departamento.objects.get(id=departamento_id)

            nome = request.POST.get('txtNome')
            
            if (nome == 'Geral'):
                messages.error(request, 'Você não pode cadastrar um departamento chamado "Geral", pois esse nome é reservado para o sistema! Use outro.')
                return redirect('cadastros:departamentos')
            
            sigla = request.POST.get('txtSigla')
            
            if Departamento.objects.filter(nome=nome).exclude(id=departamento_id).exists():
                messages.error(request, 'nome de departamento ja cadastrado nesta unidade!')
                return redirect('cadastros:departamentos')
            
            departamento.nome = nome
            departamento.sigla = sigla

            departamento.save()

            messages.success(request, 'Departamento atualizado com sucesso!')
            return redirect('cadastros:departamentos')

    departamento_lista = Departamento.objects.all().exclude(nome__iexact="Geral").order_by('nome')

    paginator = Paginator(departamento_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "departamentos.html", {'page_obj': page_obj})

@login_required
def obter_departamento_por_id(request):
    departamento_id = request.GET.get('departamento_id', None)
    departamento = Departamento.objects.get(id=departamento_id)
    
    departamento_dados = {
        'id': departamento.id,
        'nome': departamento.nome,
        'sigla': departamento.sigla,
    }

    return JsonResponse(departamento_dados)

@login_required
def excluir_departamento(request):
    if request.method == "POST":
        departamento_id = request.POST.get('departamento_id')
        departamento = Departamento.objects.filter(id=departamento_id).first()

        if (departamento.usuario_set.exists()):  
            return JsonResponse({'success': False, 'message': "Não é possível excluir o departamento, pois ele possui usuários vinculados."})

        departamento.delete()
        return JsonResponse({'success': True, 'message': 'Departamento excluído com sucesso!'})
    
    return JsonResponse({'success': False, 'message': 'Você não tem permissão para acesso.'}, status=405)
    
@login_required
def pesquisar_departamento_por_nome(request):
    departamento_nome = request.GET.get('departamento_nome', '')
    numero_pagina = request.GET.get('page')

    departamento_lista = Departamento.objects.filter(nome__icontains=departamento_nome).exclude(nome__iexact="Geral").order_by('nome')

    paginator = Paginator(departamento_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(numero_pagina)

    return JsonResponse({
        'html': render_to_string('departamentos_table.html', {'page_obj': page_obj, 'query': departamento_nome, 'request': request})
    })

#CADASTRO DE USUARIOS
@login_required
def usuarios(request):
    if request.session.get('perfil_atual') not in {'Administrador'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')

    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_usuario":
            email = request.POST.get('txtEmail')
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já está em uso!')
                return redirect('cadastros:usuarios')

            usuario = Usuario(
                nome=request.POST.get('txtNome'),
                email=email,
                departamento_id=request.POST.get('slcDepartamento')
            )
            usuario.set_password(request.POST.get('txtSenha'))
            usuario.save()
            
            perfis = request.POST.getlist('chkPerfis')
            for perfil_id in perfis:
                perfil = Perfil.objects.get(id=perfil_id)
                usuario.perfis.add(perfil)
                
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('cadastros:usuarios')

        elif acao == "alterar_usuario":
            usuario_id = request.POST.get('txtId')
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.nome = request.POST.get('txtNome')
            usuario.email = request.POST.get('txtEmail')
            usuario.departamento_id = request.POST.get('slcDepartamento')
            if request.POST.get('txtSenha'):
                usuario.set_password(request.POST.get('txtSenha'))
            usuario.save()
            
            usuario.perfis.clear()
            perfis = request.POST.getlist('chkPerfis')
            for perfil_id in perfis:
                perfil = Perfil.objects.get(id=perfil_id)
                usuario.perfis.add(perfil)

            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('cadastros:usuarios')

    usuarios_lista = Usuario.objects.all().order_by('nome').exclude(Q(id=request.session['id_atual']))
    paginator = Paginator(usuarios_lista, settings.NUMBER_GRID_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departamentos_lista = Departamento.objects.all().order_by('nome').exclude(nome__iexact="Geral")
    perfis_lista = Perfil.objects.all()

    return render(request, "usuarios.html", {
        'page_obj': page_obj,
        'perfis': perfis_lista,
        'departamentos': departamentos_lista
    })

@login_required
def verificar_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': Usuario.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

@login_required
def obter_usuario_por_id(request):
    usuario_id = request.GET.get('usuario_id', None)
    usuario = Usuario.objects.get(id=usuario_id)
    perfis_usuario = usuario.perfis.values_list('id', flat=True)
    usuario_dados = {
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'senha': '',
        'departamento_id': usuario.departamento.id,
        'perfis': list(perfis_usuario),
    }
    return JsonResponse(usuario_dados)

@login_required
def excluir_usuario(request):
    if request.method == "POST":
        usuario_id = request.POST.get('usuario_id')
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
        return JsonResponse({'success': True})

@login_required
def pesquisar_usuario_por_nome(request):
    query = request.GET.get('usuario_nome', '')
    page_number = request.GET.get('page')

    usuarios_lista = Usuario.objects.filter(nome__icontains=query).order_by('nome').exclude(Q(id=request.session['id_atual']))

    paginator = Paginator(usuarios_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        'html': render_to_string('usuarios_table.html', {'page_obj': page_obj, 'query': query, 'request': request})
    })
#----------------------------------------------------

#CADASTRO DE ATIVIDADES
@login_required
def atividades(request):
    if request.session.get('perfil_atual') not in {'Administrador'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "nova_atividade":
            nome = request.POST.get('txtNome')
            
            atividade = Atividade(
                nome=nome,
            )
            
            atividade.save()

            messages.success(request, 'Atividade cadastrada com sucesso!')
            return redirect('cadastros:atividades')

        elif acao == "alterar_atividade":
            atividade_id = request.POST.get('txtId')
            atividade = Atividade.objects.get(id=atividade_id)

            atividade.nome = request.POST.get('txtNome')
            atividade.save()

            messages.success(request, 'Atividade atualizada com sucesso!')
            return redirect('cadastros:atividades')

    atividades_lista = Atividade.objects.all().order_by('nome')

    paginator = Paginator(atividades_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "atividades.html", {'page_obj': page_obj})

@login_required
def obter_atividade_por_id(request):
    atividade_id = request.GET.get('atividade_id', None)
    atividade = Atividade.objects.get(id=atividade_id)
    
    #responsaveis
    responsaveis = atividade.responsaveis.values('id', 'nome', 'email', 'departamento__sigla').order_by('nome')
    
    atividade_dados = {
        'id': atividade.id,
        'nome': atividade.nome,
        'responsaveis': list(responsaveis),
    }

    return JsonResponse(atividade_dados)

@login_required
def excluir_atividade(request):
    if request.method == "POST":
        atividade_id = request.POST.get('atividade_id')
        atividade = Atividade.objects.filter(id=atividade_id).first()
        atividade.delete()
        
        return JsonResponse({'success': True, 'message': 'Atividade excluída com sucesso!'})
    return JsonResponse({'success': False, 'message': 'Você não tem permissão para acesso.'}, status=405)
    
@login_required
def pesquisar_atividade_por_nome(request):
    atividade_nome = request.GET.get('atividade_nome', '')
    numero_pagina = request.GET.get('page')
    
    atividades_lista = Atividade.objects.filter(nome__icontains=atividade_nome).order_by('nome')

    paginator = Paginator(atividades_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(numero_pagina)

    return JsonResponse({
        'html': render_to_string('atividades_table.html', {'page_obj': page_obj, 'query': atividade_nome, 'request': request})
    })

#RELACIONANDO ATIVIDADES COM RESPONSAVEIS (USUARIOS)
@login_required
def adicionar_responsavel_de_atividade(request):
    atividade_id = request.POST.get('atividade_id')
    responsavel_id = request.POST.get('responsavel_id')

    atividade = Atividade.objects.get(id=atividade_id)
    responsavel = Usuario.objects.get(id=responsavel_id)
    atividade.responsaveis.add(responsavel)
    
    return JsonResponse({'success': True, 'message': 'Responsavel adicionado com sucesso!'})
    
@login_required
def excluir_responsavel_de_atividade(request):
    atividade_id = request.POST.get('atividade_id')
    responsavel_id = request.POST.get('responsavel_id')

    atividade = Atividade.objects.get(id=atividade_id)
    responsavel = Usuario.objects.get(id=responsavel_id)
    atividade.responsaveis.remove(responsavel)
    
    return JsonResponse({'success': True, 'message': 'Responsavel removido com sucesso!'})

@require_POST    
@login_required
def exibir_responsaveis_possiveis_para_atividade(request):
    atividade_id = request.POST.get('txtPostIdResponsaveis')    
    responsaveis = Usuario.objects.order_by('nome').exclude(nome__iexact="Administrador")

    responsaveis_ja_associados = []
    if atividade_id:
        atividade = Atividade.objects.get(id=atividade_id)
        responsaveis_ja_associados = list(atividade.responsaveis.values_list('id', flat=True))

    paginator = Paginator(responsaveis, settings.NUMBER_GRID_MODAL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'atividade_id': atividade_id,
        'responsaveis_ja_associados': responsaveis_ja_associados
    }
    
    #carrega a pagina de adicao de responsaveis a atividades
    return render(request, 'atividades_add_responsaveis.html', context)

@login_required
def pesquisar_responsavel_por_nome_para_atividade(request):
    nome = request.GET.get('nome', '')
    page_number = request.GET.get('page', 1)
    atividade_id = request.GET.get('atividade_id', '')
    responsaveis = Usuario.objects.filter(nome__icontains=nome).order_by('nome').exclude(nome__iexact="Administrador")

    responsaveis_ja_associados = []
    if atividade_id:
        atividade = Atividade.objects.get(id=atividade_id)
        responsaveis_ja_associados = list(atividade.responsaveis.values_list('id', flat=True))

    paginator = Paginator(responsaveis, settings.NUMBER_GRID_MODAL)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'atividade_id': atividade_id,
        'responsaveis_ja_associados': responsaveis_ja_associados,
        'request': request
    }
    
    #carrega o grid com responsaveis atualizado dentro de atividades_add_responsaveis.html
    html = render_to_string('atividades_add_responsaveis_table.html', context)
    return JsonResponse({'html': html})
#----------------------------------------------------