from datetime import datetime, timezone, timedelta

# Fortaleza = UTC-3 e não usa horário de verão
FUSO_FORTALEZA = timezone(timedelta(hours=-3))


def agora():
    return datetime.now(FUSO_FORTALEZA)