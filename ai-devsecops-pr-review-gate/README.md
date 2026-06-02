# AI DevSecOps PR Review Gate

Framework interno para revisión automática de Pull Requests usando IA.

Este proyecto está inspirado en la arquitectura pública de `anthropics/claude-code-security-review`, pero está diseñado para un entorno corporativo multi-proveedor:

- Prompt packs versionados por tecnología.
- Contexto consolidado del Pull Request en `pr_context.md`.
- Proveedores IA intercambiables:
  - `github-models`
  - `openai-compatible`
  - `anthropic`
  - `gemini`
  - `mock`
- Resultado estructurado en JSON.
- Comentario automático en el PR.
- Artifact auditable.
- Gate opcional por severidad.

## Arquitectura

```text
Pull Request
   ↓
GitHub Action
   ↓
PR Context Builder
   ↓
Prompt Pack Resolver
   ↓
AI Provider Adapter
   ↓
Response Parser
   ↓
Findings Filter
   ↓
Markdown Renderer
   ↓
PR Comment + JSON Artifact + Optional Gate
```

## Outputs principales

La acción genera:

```text
pr_context.md
ai-review-result.json
ai-review-comment.md
```

Y además puede comentar automáticamente el PR.

## Uso rápido con GitHub Models

> Requiere `models: read` en permissions.

```yaml
name: AI DevSecOps PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

permissions:
  contents: read
  pull-requests: read
  issues: write
  models: read

jobs:
  ai-pr-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: TU_ORG/ai-devsecops-pr-review-gate@v1
        with:
          ai-provider: github-models
          ai-model: openai/gpt-4o
          stack: auto
          prompt-path: prompts/pullrequest/generic/security/prompt.md
          comment-pr: "true"
          fail-on-severity: critical
```

## Uso con Anthropic directo

```yaml
- uses: TU_ORG/ai-devsecops-pr-review-gate@v1
  with:
    ai-provider: anthropic
    ai-model: claude-3-5-sonnet-latest
    ai-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    stack: backend-nestjs
    prompt-path: prompts/pullrequest/backend/nestjs/prompt.md
```

## Uso con OpenAI / Azure OpenAI compatible / otros endpoints

```yaml
- uses: TU_ORG/ai-devsecops-pr-review-gate@v1
  with:
    ai-provider: openai-compatible
    ai-model: gpt-4o
    ai-api-key: ${{ secrets.AI_API_KEY }}
    ai-base-url: https://api.openai.com/v1
    prompt-path: prompts/pullrequest/generic/security/prompt.md
```

Para Azure OpenAI / Microsoft Foundry con endpoint compatible:

```yaml
- uses: TU_ORG/ai-devsecops-pr-review-gate@v1
  with:
    ai-provider: openai-compatible
    ai-model: gpt-4o
    ai-api-key: ${{ secrets.AZURE_OPENAI_API_KEY }}
    ai-base-url: https://TU-RECURSO.openai.azure.com/openai/v1
```

## Uso con repo externo de prompts

Si tu empresa maneja un repo separado como `coe-ia-prompts`:

```yaml
- uses: TU_ORG/ai-devsecops-pr-review-gate@v1
  with:
    ai-provider: github-models
    ai-model: openai/gpt-4o
    prompts-repository: TU_ORG/coe-ia-prompts
    prompts-ref: master
    prompts-token: ${{ secrets.PROMPTS_REPO_TOKEN }}
    prompt-path: pullrequest/backend/nestjs/prompt.md
```

## Estructura de prompts recomendada

```text
prompts/
└── pullrequest/
    ├── backend/
    │   ├── nestjs/
    │   │   └── prompt.md
    │   └── go/
    │       └── prompt.md
    ├── infrastructure/
    │   └── terraform/
    │       └── prompt.md
    └── generic/
        └── security/
            └── prompt.md
```

## Formato de prompt

Cada prompt puede tener front matter:

```yaml
---
provider: github-models
model: openai/gpt-4o
reviewType: pullrequest
stack: backend-nestjs
responseFormat: json
---
```

Luego el contenido del prompt.

## Resultado JSON esperado

```json
{
  "summary": "Resumen general",
  "impact_score": 4,
  "quality_score": "B",
  "findings": [
    {
      "title": "Falta validación de autorización",
      "severity": "high",
      "confidence": "high",
      "file": "src/users/user.controller.ts",
      "line": 42,
      "category": "Authorization",
      "description": "El endpoint permite acceder a recursos sin validar ownership.",
      "recommendation": "Validar que el usuario autenticado tenga permiso sobre el recurso.",
      "cwe": "CWE-862"
    }
  ],
  "positive_points": [],
  "critical_violations": []
}
```

## Seguridad

- No ejecutar código del PR.
- Analizar únicamente diff y contexto controlado.
- Evitar `pull_request_target` salvo diseño seguro.
- Usar permisos mínimos.
- No enviar secretos a proveedores externos.
- Usar proveedores aprobados por la organización.
- Guardar evidencia para auditoría.

## Roadmap sugerido

- Comentarios inline por línea.
- Integración con Snyk.
- Integración con tfsec/Checkov.
- Integración con CodeQL.
- Dashboard de métricas.
- Prompt packs por squad/repo.
- Control de falsos positivos por repositorio.
