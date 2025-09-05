# Sistema de Logging Moderno

Este diretório contém o sistema de logging moderno da aplicação, que substitui o antigo `applog.py`.

## Estrutura

```
core/logging/
├── __init__.py      # Interface principal
├── config.py        # Configuração e setup
├── formatters.py    # Formatadores customizados
├── handlers.py      # Handlers customizados
└── utils.py         # Utilitários e decorators
```

## Uso Básico

### Setup (uma vez na aplicação)

```python
from core.logging import setup_logging

# No início da aplicação (main.py)
setup_logging("INFO")  # ou DEBUG, WARNING, ERROR
```

### Uso em módulos

```python
from core.logging import get_logger

# Em cada módulo
logger = get_logger(__name__)

logger.info("Aplicação iniciada")
logger.error("Erro encontrado", exc_info=True)
```

## Recursos Avançados

### Logging Estruturado

```python
logger.info("Login realizado", extra={
    'user_id': '12345',
    'ip_address': '192.168.1.1',
    'success': True
})
```

### Decorators de Performance

```python
from core.logging.utils import log_execution_time

@log_execution_time('performance')
def operacao_lenta():
    # código aqui
    pass
```

### Context Managers

```python
from core.logging.utils import LogContext

with LogContext('app', request_id='req-123'):
    logger.info("Processando request")
```

### Classes com Logging

```python
from core.logging import LoggerMixin

class MinhaClasse(LoggerMixin):
    def metodo(self):
        self.logger.info("Método executado")
```

## Configuração

O sistema suporta:

- **Múltiplos handlers**: Console, arquivo, erro
- **Rotação de logs**: Arquivos limitados em tamanho
- **Formatação flexível**: Texto simples, detalhado, JSON
- **Níveis configuráveis**: DEBUG, INFO, WARNING, ERROR
- **Logging assíncrono**: Para alta performance

## Migração do applog.py

### Antes (deprecated)
```python
from applog import logger
logger.info("mensagem")
```

### Depois (moderno)
```python
from core.logging import get_logger
logger = get_logger(__name__)
logger.info("mensagem")
```

## Arquivos de Log

- `logs/app.log` - Log geral da aplicação
- `logs/error.log` - Apenas erros e críticos

Os logs são rotacionados automaticamente quando atingem 10MB.

## Exemplo Completo

Veja `logging_examples.py` para exemplos práticos de uso.
