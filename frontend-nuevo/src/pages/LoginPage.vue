<template>
  <div class="login-background full-height">
    <div class="login-overlay"></div>

    <div class="login-shell row no-wrap items-center justify-center full-height">
      <div class="login-panel row no-wrap shadow-2">
        <div class="login-form-column column q-pa-xl q-gutter-md">
          <div class="brand-header column q-mb-xl text-center">
            <div class="text-h5 brand-title">Bobinados</div>
            <div class="text-body2 brand-subtitle q-mt-sm">Control industrial con respaldo digital</div>
          </div>

          <q-card square bordered class="q-pa-lg shadow-1 login-card">
            <div class="text-h6 text-center q-mb-md">Inicia sesión en tu cuenta</div>
            <p class="text-body2 text-center text-weight-medium text-dark-5 q-mb-lg">
              Accede al panel de usuarios y gestión con seguridad industrial.
            </p>

            <q-form @submit.prevent="login" ref="form_login">
              <q-card-section>
                <q-input
                  square filled clearable
                  v-model="login_form.username"
                  label="Usuario"
                  class="q-mb-sm"
                />

                <q-input
                  square filled clearable
                  v-model="login_form.password"
                  type="password"
                  label="Contraseña"
                />
              </q-card-section>

              <q-card-actions class="q-px-md">
                <q-btn
                  type="submit"
                  unelevated
                  color="accent"
                  size="lg"
                  class="full-width accent-btn"
                  label="INICIAR SESIÓN"
                  :loading="loading"
                  :disable="loading"
                />
              </q-card-actions>

              <q-separator class="q-my-md" />

              <div class="text-center q-mt-md">
                <a href="#" @click="openModal()">¿Olvidaste tu contraseña?</a>
              </div>
            </q-form>

            <div class="login-card-logo-wrap q-mt-lg q-mb-sm">
              <img src="/logo.png" class="login-card-logo" alt="Bobinados logo">
            </div>

            <q-banner
              v-if="error_login"
              class="bg-negative text-white q-mt-md"
            >
              {{ error_login }}
            </q-banner>
          </q-card>
        </div>

        <div class="login-hero-column column">
          <div class="hero-content">
            <div class="hero-title text-white">Sistema de control industrial</div>
            <div class="hero-copy text-white q-mt-md">
              Gestiona usuarios, accesos y módulos con una experiencia enfocada en el sector industrial.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL RECUPERAR CONTRASEÑA -->
    <q-dialog v-model="modalOlvidasteContrasena" persistent>
      <q-card style="min-width: 300px">
        <q-card-section class="row items-center">
          <div class="text-h6 q-pa-md">Recuperar contraseña</div>
          <p class="text-body2 q-px-md">
            Por favor, ingrese la dirección de correo electrónico que utilizó al registrarse para que podamos enviarle una nueva contraseña.
          </p>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="email_olvidaste_contrasena"
            label="Correo electrónico"
            type="email"
            clearable
            filled
            square
            autofocus
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn elevated color="red" label="Cancelar" v-close-popup />
          <q-btn elevated color="secondary" label="Enviar enlace" :loading="loading" @click="submitReset()" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
// === IMPORTS ===
import { AbilityBuilder } from '@casl/ability'
import { useAuthStore } from 'src/stores/auth';
import { useRouter } from 'vue-router';
import { ref, watch } from 'vue'
import { ability } from 'src/services/ability';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar'

// === STORE / ROUTER ===
const auth = useAuthStore()
const router = useRouter()
const $q = useQuasar()

// === VARIABLES ===
const form_login = ref(null)
const login_form = ref({ username: '', password: '' })
const loading = ref(false)
const error_login = ref('')

const modalOlvidasteContrasena = ref(false)
const email_olvidaste_contrasena = ref('')

// === LOGIN ===
async function login() {
  if (!login_form.value.username || !login_form.value.password) {
    $q.notify({
      type: 'warning',
      message: 'Por favor ingresa tu usuario y contraseña.',
      position: 'top',
    })
    return
  }

  try {
    loading.value = true
    await auth.login(login_form.value)
    router.push({ name: 'index' })
  } catch (error) {
    if (error.response && [400, 401].includes(error.response.status)) {
      error_login.value = 'Usuario o contraseña incorrectos'
    } else {
      error_login.value = 'Error de conexión'
    }
  } finally {
    loading.value = false
  }
}

// === RECUPERAR CONTRASEÑA ===
function openModal() {
  email_olvidaste_contrasena.value = ''
  modalOlvidasteContrasena.value = true
}

async function submitReset() {
  if (!email_olvidaste_contrasena.value) {
    $q.notify({ type: 'warning', message: 'Por favor ingresa tu correo.' })
    return
  }

  loading.value = true
  try {
    const response = await api.post('/seguridad/verificar_correo/', {
      email: email_olvidaste_contrasena.value
    })

    if (!response) {
      $q.notify({ type: 'negative', message: 'Error al enviar el enlace.' })
      return
    }

    $q.notify({
      type: 'positive',
      message: `Se envió la nueva contraseña a: ${email_olvidaste_contrasena.value}`,
      position: 'top',
      textColor: 'black',
      icon: 'check_circle',
    })

    modalOlvidasteContrasena.value = false
  } finally {
    loading.value = false
  }
}

// === CASL ===
function setRoleAbilities(rol) {
  const { can, rules } = new AbilityBuilder(ability.constructor)

  switch (rol) {
    case 'AD':
      can('manage', 'all')
      break
    case 'CO':
      can(['read'], ['Programacion', 'Corte', 'Presentacion', 'Lavanderia', 'Inventario'])
      can(['create', 'update', 'delete', 'detail', 'finish'], 'Corte')
      // el acceso a inicio/parametros/usuarios se controla por sujeto explícito
      break
    case 'IN':
      can(['read'], ['Programacion', 'Corte', 'Presentacion', 'Lavanderia', 'Inventario'])
      can(['create', 'update', 'delete', 'detail', 'finish'], 'Programacion')
      break
    case 'PR':
      can(['read'], ['Corte', 'Programacion', 'Lavanderia', 'Presentacion', 'Inventario'])
      can(['create', 'update', 'delete', 'detail', 'finish'], ['Lavanderia', 'Presentacion'])
      break
    case 'PL':
      can(['read'], ['Corte', 'Programacion', 'Lavanderia', 'Presentacion', 'Inventario'])
      can(['create', 'update', 'delete', 'detail', 'finish'], 'Corte')
      break
    default:
      // Sin acceso por defecto
      break
  }

  ability.update(rules)
}

watch(
  () => auth.rol,
  (newRol) => {
    setRoleAbilities(newRol)
  }
)

// Limpia el mensaje de error al escribir
watch([() => login_form.value.username, () => login_form.value.password], () => {
  error_login.value = ''
})
</script>

<style lang="scss">
.login-background {
  position: relative;
  background-image: url('/bg-textil.jpeg');
  background-size: cover;
  background-position: center;
  min-height: 100vh;
  overflow: hidden;
}

.login-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 51, 102, 0.84), rgba(0, 20, 40, 0.64));
  z-index: 1;
}

.login-shell {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  width: 100%;
  padding: 24px;
}

.login-panel {
  max-width: 1160px;
  width: 100%;
  border-radius: 28px;
  overflow: hidden;
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(18px);
}

.login-form-column {
  width: 420px;
  min-width: 320px;
  padding: 48px 36px;
  background: rgba(255,255,255,0.94);
}

.brand-header {
  gap: 16px;
}

.login-brand-logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
  border-radius: 16px;
  padding: 10px;
  background: rgba(212,175,55,0.12);
}

.brand-title {
  font-weight: 800;
}

.brand-subtitle {
  opacity: 0.8;
}

.login-card {
  width: 100%;
  border-radius: 20px;
  border-top: 6px solid var(--bobinados-accent) !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.94));
  box-shadow: 0 18px 44px rgba(0,0,0,0.16);
}

.login-hero-column {
  flex: 1;
  min-height: 560px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: linear-gradient(135deg, rgba(0,0,0,0.62), rgba(0,0,0,0.24)), url('/bg-textil.jpeg');
  background-size: cover;
  background-position: center right;
  padding: 40px;
}

.hero-content {
  max-width: 520px;
  text-align: left;
}

.hero-chip {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(212,175,55,0.14);
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.6px;
  margin-bottom: 18px;
}

.hero-title {
  font-size: 2.6rem;
  font-weight: 800;
  line-height: 1.05;
  text-shadow: 0 20px 40px rgba(0, 0, 0, 0.22);
}

.hero-copy {
  max-width: 500px;
  opacity: 0.95;
  line-height: 1.8;
  text-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
}

.login-card-logo-wrap {
  display: flex;
  justify-content: center;
}

.login-card-logo {
  width: 120px;
  border-radius: 18px;
  background: rgba(255,255,255,0.92);
  padding: 14px;
  box-shadow: 0 14px 28px rgba(0,0,0,0.18);
}

.login-logo {
  width: 140px;
  display: block;
  margin: 6px auto 18px auto;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.18));
}

.full-height {
  height: 100vh;
}

@media (max-width: 1024px) {
  .login-panel {
    flex-direction: column;
    border-radius: 24px;
  }

  .login-form-column,
  .login-hero-column {
    width: 100%;
    min-width: auto;
  }

  .login-hero-column {
    min-height: 360px;
    padding: 32px;
  }
}

@media (max-width: 720px) {
  .login-shell {
    padding: 16px;
  }

  .login-card {
    border-radius: 16px;
  }

  .hero-title {
    font-size: 2rem;
  }
}
</style>

