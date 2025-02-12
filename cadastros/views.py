from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import (
    Q,
    F,
    Count,
    Subquery,
    OuterRef,
    FloatField,
    Sum,
    ExpressionWrapper,
)
from .models import Usuario, Perfil, Departamento
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# CADASTRO DE DEPARTAMENTOS
@login_required  # decorator import, bloquear acesso sem login
def departamentos(request):  # funcao para url departamento
    if request.session.get("perfil_atual") not in {"Administrador"}:
        messages.error(request, "Você não é Administrador!")
        return redirect("core:main")  # vai pra view main de core
    acao = request.POST.get("btnAcao")
    if request.method == "POST":
        if acao == "novo_departamento":
            nome = request.POST.get("txtNome")
            if nome == "Geral":
                messages.error(
                    request,
                    'Você não pode cadastrar um departamento chamado "GERAL", use outro!',
                )
                return redirect("cadastros:departamentos")
            sigla = request.POST.get("txtSigla")
            if Departamento.objects.filter(
                nome=nome
            ).exists():  # pra ver se o nome ja existe
                messages.error(request, "Já existe um departamento com esse nome!")
                return redirect("cadastros:departamentos")

            departamento = Departamento(nome=nome, sigla=sigla)

            departamento.save()

            messages.success(request, "Departamento cadastrado com sucesso!")
            return redirect("cadastros:departamentos")

        elif acao == "alterar_departamento":
            departamento_id = request.POST.get("txtId")
            departamento = Departamento.objects.get(id=departamento_id)

            nome = request.POST.get("txtNome")
            if nome == "Geral" or Departamento.objects.filter(nome=nome).exists():
                messages.error(
                    request,
                    "Esse nome não pode ser escolhido!",
                )
            sigla = request.POST.get("txtSigla")

            departamento.nome = nome
            departamento.sigla = sigla
            departamento.save()

            messages.success(request, "Departamento alterado com sucesso!")
            return redirect("cadastros:departamentos")

    # pegando todos os departamentos menos o geral (dpto "fantasma" criado em commands da pasta sistema)
    departamento_lista = (
        Departamento.objects.all().exclude(nome__iexact="Geral").order_by("nome")
    )
    paginator = Paginator(departamento_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get("page")
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "departamentos.html", {"page_obj": page_obj})


@login_required
def obter_departamento_por_id(request):
    departamento_id = request.GET.get("departamento_id", None)
    departamento = Departamento.objects.get(id=departamento_id)

    # construir json
    departamento_dados = {
        "id": departamento.id,
        "nome": departamento.nome,
        "sigla": departamento.sigla,
    }

    return JsonResponse(departamento_dados)
