#!/bin/bash
set -e

cd `dirname $0`

if [ -z "$PYTHON" ]; then
  PYTHON=`which python3`
fi

build() {
  # la accion por defecto es reconstruir el virtual env
  if ! test -d ".venv"; then
    if ! $PYTHON -m virtualenv --version -q; then
      echo "Debe instalar virtualenv en python3"
      echo sudo python3 -m pip install virtualenv
    fi
    $PYTHON -m virtualenv -p $PYTHON --download .venv
  fi

  .venv/bin/pip install -r requirements-dev.txt
  .venv/bin/pip freeze | sort > .venv/freezed_after_create.log
}

clean() {
  rm -rf .venv
}

if test "$1" = "clean"; then
  clean
	exit 0
fi

if test "$1" = "freeze"; then
  .venv/bin/pip freeze > python_freezed_$(date +'%Y%m%d_%H%M%S').log
	exit 0
fi

if test "$1" = "freeze_diff"; then
  .venv/bin/pip freeze | sort > .venv/freeze_diff_local
  diff .venv/freezed_after_create.log .venv/freeze_diff_local
	exit 0
fi

if test "$1" = "build"; then
  build
  exit 0
fi

if test "$1" = "rebuild"; then
  clean
  build
  exit 0
fi

if test "$1" = "install"; then
  .venv/bin/pip install "$2"
	exit 0
fi


echo "Uso:
buid            Crea el virtua env si aun no esta creado
rebuild         Re crea el virtual env eliminando el actual y volviendo a crearlo
clean           Elimina el virtual env
freeze          Freeza todas las dependencias en python_freezed_*.log
freeze_diff     Lista las diferencias entre el virtualenv actual y el que fue instalado, util para ver que dependencias agregar al requirements.txt
install modulo  Instala un modulo en el virtual env
"
