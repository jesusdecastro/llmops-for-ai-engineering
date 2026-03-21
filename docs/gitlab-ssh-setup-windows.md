# Configuración SSH para GitLab en Windows

Guía paso a paso para registrar una SSH key en GitLab (gitlabdes.hiberus.com)

---

## 📋 Paso 1: Verificar SSH Existente

Abre PowerShell y ejecuta:

```powershell
# Ver si ya tienes keys
ls $env:USERPROFILE\.ssh\
```

**Deberías ver archivos como:**
- `id_ed25519` (private key)
- `id_ed25519.pub` (public key)

Si no existen, ve al **Paso 2**. Si existen, ve al **Paso 3**.

---

## 🔑 Paso 2: Generar Nueva SSH Key (Si no tienes)

```powershell
# Generar ED25519 key (recomendado)
ssh-keygen -t ed25519 -C "tu.email@hiberus.com"
```

**Responde a las preguntas:**

```
Enter file in which to save the key (/c/Users/jsdecastro/.ssh/id_ed25519):
[Presiona ENTER para aceptar la ruta por defecto]

Enter passphrase (empty for no passphrase):
[Escribe una contraseña segura o presiona ENTER para sin contraseña]

Enter same passphrase again:
[Repite la contraseña]
```

**Resultado esperado:**
```
Your identification has been saved in /c/Users/jsdecastro/.ssh/id_ed25519
Your public key has been saved in /c/Users/jsdecastro/.ssh/id_ed25519.pub
```

---

## 📋 Paso 3: Copiar la Clave Pública

Ejecuta este comando para copiar tu clave pública al portapapeles:

```powershell
# Copiar clave pública
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard

Write-Host "✅ Clave pública copiada al portapapeles"
```

**Verifica que se copió correctamente:**

```powershell
# Ver el contenido
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

**Deberías ver algo como:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKx... tu.email@hiberus.com
```

---

## 🌐 Paso 4: Registrar en GitLab

### 4.1 Acceder a GitLab

1. Abre tu navegador
2. Ve a: `https://gitlabdes.hiberus.com`
3. Inicia sesión con tu usuario de Hiberus

### 4.2 Ir a SSH Keys

1. Click en tu **avatar** (esquina superior derecha)
2. Selecciona **Edit profile**
3. En la barra lateral izquierda, click en **SSH Keys**

### 4.3 Agregar Nueva Key

1. Click en **Add new key**
2. En el campo **Key**, pega tu clave pública (ya está en portapapeles)
   - Presiona `Ctrl+V` para pegar
3. En el campo **Title**, escribe una descripción:
   ```
   Windows Laptop - jsdecastro
   ```
4. **Usage type**: Selecciona `Authentication & Signing` (para commits firmados)
5. **Expiration date**: Deja vacío o selecciona fecha (ej: 1 año)
6. Click en **Add key**

**Deberías ver un mensaje de éxito:**
```
SSH key was successfully added
```

---

## ✅ Paso 5: Verificar la Conexión

Abre PowerShell y ejecuta:

```powershell
# Probar conexión SSH
ssh -T git@gitlabdes.hiberus.com
```

**Primera vez:** Verás un mensaje preguntando si confías en el host:

```
The authenticity of host 'gitlabdes.hiberus.com (IP)' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)?
```

Escribe: `yes` y presiona ENTER

**Resultado esperado:**
```
Welcome to GitLab, @tu_usuario!
```

Si ves esto, ¡tu SSH está configurada correctamente! ✅

---

## 🐛 Troubleshooting

### Problema 1: "Permission denied (publickey)"

**Causa:** La key no está registrada en GitLab o hay un problema con permisos.

**Solución:**

```powershell
# 1. Verificar que la key está en ssh-agent
ssh-add -l

# Si no aparece, agregarla:
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# 2. Verificar que está en GitLab
# Ve a GitLab → Edit profile → SSH Keys
# Verifica que tu key está listada
```

### Problema 2: "Could not open a connection to your authentication agent"

**Causa:** ssh-agent no está corriendo.

**Solución:**

```powershell
# Iniciar ssh-agent
Start-Service ssh-agent

# Agregar key
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

### Problema 3: "Bad configuration option" en SSH config

**Causa:** Archivo config tiene BOM (Byte Order Mark).

**Solución:**

```powershell
# Reparar archivo config
$content = Get-Content $env:USERPROFILE\.ssh\config -Raw
if ($content.StartsWith([char]0xFEFF)) {
    $content = $content.Substring(1)
}
[System.IO.File]::WriteAllText("$env:USERPROFILE\.ssh\config", $content, [System.Text.UTF8Encoding]$false)

Write-Host "✅ SSH config reparado"
```

### Problema 4: "Host key verification failed"

**Causa:** Primera conexión, necesita confirmar fingerprint.

**Solución:**

```powershell
# Ejecutar y responder "yes"
ssh -T git@gitlabdes.hiberus.com
```

---

## 🔐 Paso 6: Configurar SSH Config (Opcional pero Recomendado)

Crea/edita el archivo `~/.ssh/config`:

```powershell
# Abrir con Notepad
notepad $env:USERPROFILE\.ssh\config
```

Agrega esto (sin BOM):

```
Host gitlabdes.hiberus.com
    HostName gitlabdes.hiberus.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

**Importante:** Guarda como **UTF-8 sin BOM** (no UTF-8 con BOM)

En Notepad:
1. File → Save As
2. Encoding: **UTF-8** (no UTF-8 BOM)
3. Save

---

## 🚀 Paso 7: Clonar Repositorio

Ahora ya puedes clonar:

```powershell
cd C:\Users\jsdecastro\repositories_architecture

git clone git@gitlabdes.hiberus.com:data-ia_dga/data-ia_dgagricultura/iavedo-ia-infra.git
```

**Resultado esperado:**
```
Cloning into 'iavedo-ia-infra'...
remote: Enumerating objects: 123, done.
remote: Counting objects: 100% (123/123), done.
...
```

---

## ✅ Checklist Final

- [ ] SSH key generada (ED25519)
- [ ] Clave pública copiada
- [ ] Registrada en GitLab (Edit profile → SSH Keys)
- [ ] Conexión verificada (`ssh -T git@gitlabdes.hiberus.com`)
- [ ] SSH config creado (sin BOM)
- [ ] Repositorio clonado exitosamente

---

## 📚 Comandos Útiles

```powershell
# Ver todas tus keys
ssh-add -l

# Agregar key a ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# Remover key de ssh-agent
ssh-remove $env:USERPROFILE\.ssh\id_ed25519

# Ver fingerprint de tu key
ssh-keygen -l -f $env:USERPROFILE\.ssh\id_ed25519.pub

# Probar conexión con verbose
ssh -vvv git@gitlabdes.hiberus.com
```

---

## 🔒 Seguridad

**Buenas prácticas:**

1. ✅ Usa ED25519 (más seguro que RSA)
2. ✅ Protege tu private key con passphrase
3. ✅ Nunca compartas tu private key
4. ✅ Revoca keys comprometidas en GitLab
5. ✅ Usa expiration dates en GitLab
6. ✅ Revisa regularmente tus keys en GitLab

---

## 🆘 Soporte

Si tienes problemas:

1. Verifica que estás en la red de Hiberus (o VPN)
2. Contacta a IT si gitlabdes.hiberus.com no es accesible
3. Verifica que tu usuario tiene acceso al proyecto
4. Revisa los logs: `ssh -vvv git@gitlabdes.hiberus.com`

---

**Última actualización:** Febrero 2026
