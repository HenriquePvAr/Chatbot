from collections import deque
from threading import Condition, Thread
from time import monotonic
from concurrent.futures import ThreadPoolExecutor


class FilaMensagens:
    """Fila justa por conversa, com limite de rajada e processamento paralelo."""

    def __init__(
        self,
        *,
        trabalhadores=2,
        rajada_por_usuario=3,
        pausa_segundos=5.0,
        maximo_por_usuario=30,
        maximo_total=2000,
        relogio=monotonic,
    ):
        if trabalhadores < 1 or rajada_por_usuario < 1:
            raise ValueError("Trabalhadores e tamanho da rajada devem ser positivos.")
        if pausa_segundos < 0 or maximo_por_usuario < 1 or maximo_total < 1:
            raise ValueError("Limites da fila invalidos.")

        self.trabalhadores = trabalhadores
        self.rajada_por_usuario = rajada_por_usuario
        self.pausa_segundos = pausa_segundos
        self.maximo_por_usuario = maximo_por_usuario
        self.maximo_total = maximo_total
        self._relogio = relogio

        self._condicao = Condition()
        self._filas = {}
        self._ordem = deque()
        self._agendados = set()
        self._em_andamento = set()
        self._rajadas = {}
        self._liberado_em = {}
        self._pendentes = 0
        self._encerrar = False
        self._executor = None
        self._despachante = None
        self._processador = None
        self._ao_falhar = None

    def iniciar(self, processador, ao_falhar=None):
        with self._condicao:
            if self._despachante is not None:
                return
            self._processador = processador
            self._ao_falhar = ao_falhar
            self._executor = ThreadPoolExecutor(
                max_workers=self.trabalhadores,
                thread_name_prefix="whatsapp-resposta",
            )
            self._despachante = Thread(
                target=self._despachar,
                name="whatsapp-fila",
                daemon=True,
            )
            self._despachante.start()

    def enviar(self, usuario, item):
        with self._condicao:
            fila = self._filas.get(usuario)
            if fila is None:
                fila = deque()
                self._filas[usuario] = fila
            if len(fila) >= self.maximo_por_usuario or self._pendentes >= self.maximo_total:
                if not fila and usuario not in self._em_andamento:
                    self._filas.pop(usuario, None)
                return False

            fila.append(item)
            self._pendentes += 1
            self._agendar(usuario)
            self._condicao.notify_all()
            return True

    def _agendar(self, usuario):
        fila = self._filas.get(usuario)
        if (
            fila
            and usuario not in self._em_andamento
            and usuario not in self._agendados
        ):
            self._ordem.append(usuario)
            self._agendados.add(usuario)

    def _despachar(self):
        while True:
            with self._condicao:
                if self._encerrar:
                    return

                usuario, item = self._proximo_pronto()
                if usuario is None:
                    self._condicao.wait(timeout=self._tempo_ate_proximo())
                    continue

                self._em_andamento.add(usuario)
                self._pendentes -= 1

            self._executor.submit(self._processar, usuario, item)

    def _proximo_pronto(self):
        quantidade = len(self._ordem)
        agora = self._relogio()
        for _ in range(quantidade):
            usuario = self._ordem.popleft()
            self._agendados.discard(usuario)

            if usuario in self._em_andamento:
                continue

            fila = self._filas.get(usuario)
            if not fila:
                self._filas.pop(usuario, None)
                continue

            if self._liberado_em.get(usuario, 0) > agora:
                self._agendar(usuario)
                continue

            item = fila.popleft()
            return usuario, item
        return None, None

    def _tempo_ate_proximo(self):
        agora = self._relogio()
        tempos = [
            max(0.0, self._liberado_em.get(usuario, 0) - agora)
            for usuario in self._agendados
            if self._filas.get(usuario)
        ]
        return min(tempos) if tempos else None

    def _processar(self, usuario, item):
        try:
            self._processador(item)
        except Exception as erro:
            if self._ao_falhar is not None:
                try:
                    self._ao_falhar(item, erro)
                except Exception:
                    pass
        finally:
            with self._condicao:
                self._em_andamento.discard(usuario)
                fila = self._filas.get(usuario)
                if fila:
                    proxima_rajada = self._rajadas.get(usuario, 0) + 1
                    if proxima_rajada >= self.rajada_por_usuario:
                        self._rajadas[usuario] = 0
                        self._liberado_em[usuario] = (
                            self._relogio() + self.pausa_segundos
                        )
                    else:
                        self._rajadas[usuario] = proxima_rajada
                    self._agendar(usuario)
                else:
                    self._filas.pop(usuario, None)
                    self._rajadas.pop(usuario, None)
                    self._liberado_em.pop(usuario, None)
                self._condicao.notify_all()

    def esperar_vazia(self, timeout=None):
        fim = None if timeout is None else self._relogio() + timeout
        with self._condicao:
            while self._pendentes or self._em_andamento:
                restante = None if fim is None else fim - self._relogio()
                if restante is not None and restante <= 0:
                    return False
                self._condicao.wait(timeout=restante)
            return True

    def estado(self):
        with self._condicao:
            return {
                "pendentes": self._pendentes,
                "em_andamento": len(self._em_andamento),
                "usuarios_na_fila": sum(bool(fila) for fila in self._filas.values()),
            }

    def parar(self, aguardar=True):
        with self._condicao:
            self._encerrar = True
            self._condicao.notify_all()
        if self._despachante is not None:
            self._despachante.join(timeout=5)
        if self._executor is not None:
            self._executor.shutdown(wait=aguardar, cancel_futures=not aguardar)
