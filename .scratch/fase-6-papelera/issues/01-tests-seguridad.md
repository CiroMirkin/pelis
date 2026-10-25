# Tests de seguridad de la papelera, antes de cualquier movido o borrado

Status: ready-for-agent

Requisito previo de la spec: ningún código que mueva o borre carpetas se escribe antes de estos tests. Usar una biblioteca temporal (`tmp_path`) con varias carpetas hermanas.

## Criterio de terminado
- [ ] Mover a la papelera mueve solo la carpeta de la película indicada (por `id`/`folder_path`)
- [ ] Las carpetas hermanas quedan intactas
- [ ] La purga al vencer los 7 días no borra nada fuera de `.papelera/`, ni otras carpetas dentro de ella que no hayan vencido
- [ ] Los tests corren en rojo hasta que exista la implementación
