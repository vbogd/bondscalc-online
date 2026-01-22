# Как запустить

Вместо `podman` можно использовать `docker`.

```shell
podman build -t bondscalc .
podman run --name bondscalc --rm -e TZ=Europe/Moscow -p 0.0.0.0:8050:8050 bondscalc
```
