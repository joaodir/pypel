from django.urls import path
from . import views

app_name = 'cadastros'

urlpatterns = [

    #CADASTRO DE DEPARTAMENTOS
    path('departamentos/', views.departamentos, name='departamentos'),
    path('obter_departamento_por_id/', views.obter_departamento_por_id, name='obter_departamento_por_id'),
    path('excluir_departamento/', views.excluir_departamento, name='excluir_departamento'),
    path('pesquisar_departamento_por_nome/', views.pesquisar_departamento_por_nome, name='pesquisar_departamento_por_nome'),
    #---------------------------------------------
    
    #CADASTRO DE USUARIOS
    path("usuarios/", views.usuarios, name="usuarios"),
    path('verificar_email/', views.verificar_email, name='verificar_email'),
    path('obter_usuario_por_id/', views.obter_usuario_por_id, name='obter_usuario_por_id'),
    path('excluir_usuario/', views.excluir_usuario, name='excluir_usuario'),
    path('pesquisar_usuario_por_nome/', views.pesquisar_usuario_por_nome, name='pesquisar_usuario_por_nome'),
    #---------------------------------------------
    
    #CADASTRO DE ATIVIDADES
    path('atividades/', views.atividades, name='atividades'),
    path('obter_atividade_por_id/', views.obter_atividade_por_id, name='obter_atividade_por_id'),
    path('excluir_atividade/', views.excluir_atividade, name='excluir_atividade'),
    path('pesquisar_atividade_por_nome/', views.pesquisar_atividade_por_nome, name='pesquisar_atividade_por_nome'),
    
    #RELACIONANDO ATIVIDADES COM RESPONSAVEIS (USUARIOS)
    path('adicionar_responsavel_de_atividade/', views.adicionar_responsavel_de_atividade, name='adicionar_responsavel_de_atividade'),
    path('excluir_responsavel_de_atividade/', views.excluir_responsavel_de_atividade, name='excluir_responsavel_de_atividade'),
    path('exibir_responsaveis_possiveis_para_atividade/', views.exibir_responsaveis_possiveis_para_atividade, name='exibir_responsaveis_possiveis_para_atividade'),
    path('pesquisar_responsavel_por_nome_para_atividade/', views.pesquisar_responsavel_por_nome_para_atividade, name='pesquisar_responsavel_por_nome_para_atividade'),
    #---------------------------------------------
    
]

